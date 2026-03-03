from typing import Annotated, Optional

import dagger
from dagger import DefaultPath, Doc, dag, function, object_type


@object_type
class SportsAnalyticsCi:
    @function
    async def publish(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Doc("Source code directory")],
        branch_name: Annotated[
            Optional[str],
            Doc("Current working branch != main -> not a production image"),
        ],
        github_sa_key: Annotated[Optional[dagger.Secret], Doc("SSH key for GitHub authentication")],
        registry_token: Annotated[
            Optional[dagger.Secret], Doc("Token for authentication on container registry")
        ],
        registry_username: Annotated[
            Optional[str], Doc("Username for authentication on container registry")
        ],
        registry_url: Annotated[Optional[str], Doc("Container registry URL")] = "",
    ) -> list[str]:
        """Publish the application container after building and testing it on-the-fly"""
        addr = []

        runtime_image = await self.build(source)

        # Get tags dynamically
        commit_sha = await self.git_sha(source)
        app_version = await self.app_version(source)

        # Setting registry url to local registry if it's empty
        if registry_url:
            runtime_image = runtime_image.with_registry_auth(
                registry_url, registry_username, registry_token
            )
        else:
            registry_url = "ttl.sh"

        # Parse Git ref to branch name
        if branch_name == "main":
            tags = [commit_sha, app_version, "main"]
            await self.git_tagger(source, tag=app_version, github_sa_key=github_sa_key)
        elif branch_name is not None:
            branch_name = branch_name.replace("/", "-")
            tags = [commit_sha, branch_name, "dev"]
        else:
            tags = [commit_sha]

        for tag in tags:
            a = await runtime_image.publish(f"{registry_url}/sports-analytics:{tag}")
            addr.append(a)

        return addr

    @function
    def build(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Doc("Source code directory")],
    ) -> dagger.Container:
        """Build the application runtime container"""
        builder = self.build_env(source)

        return (
            dag.container()
            .from_("python:3.13-slim-bookworm")
            .with_directory("/app", builder.directory("/app"))
            .with_workdir("/app")
            .with_env_variable("PATH", "/app/.venv/bin:$PATH", expand=True)
            .with_exposed_port(80)
        )

    @function
    def build_env(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Doc("Source code directory")],
    ) -> dagger.Container:
        """Build a ready-to-use development environment"""
        uv_cache = dag.cache_volume("uv-cache")
        dbt_home = dag.cache_volume("dbt-home")

        base = (
            dag.container()
            .from_("ghcr.io/astral-sh/uv:python3.13-bookworm-slim")
            .with_workdir("/app")
            .with_env_variable("UV_COMPILE_BYTECODE", "1")
            .with_mounted_cache("/root/.cache/uv", uv_cache)
            .with_mounted_cache("/root/.dbt", dbt_home)
        )

        deps = base.with_directory(
            "/app",
            dag.directory()
            .with_file("pyproject.toml", source.file("pyproject.toml"))
            .with_file("uv.lock", source.file("uv.lock")),
        ).with_exec(["uv", "sync", "--frozen", "--no-install-project", "--no-dev"])

        return (
            deps.with_directory("/app", source.directory("/src"))
            .with_file("uv.lock", source.file("uv.lock"))
            .with_exec(["uv", "sync", "--frozen", "--no-dev", "--package", "sports_analytics"])
            .with_env_variable("DBT_TARGET", "ci")
            .with_env_variable("PATH", "/app/.venv/bin:$PATH", expand=True)
            .with_env_variable("HOME", "/root")
            .with_exec(
                [
                    "dagster-dbt",
                    "project",
                    "prepare-and-package",
                    "--file",
                    "/app/sports_analytics/defs/project.py",
                ]
            )
        )

    @function
    async def git_container(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Doc("Source code directory")],
    ) -> dagger.Container:
        """Returns a container which is prepared for git operations"""
        base = (
            dag.container()
            .from_("alpine:3")
            .with_workdir("/app")
            .with_directory("/app", source)
            .with_exec(["apk", "add", "--no-cache", "git", "openssh"])
        )

        return base

    @function
    async def git_sha(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Doc("Source code directory")],
    ) -> str:
        """Returns the commit SHA of the most recent commit (HEAD)"""
        git_container = await self.git_container(source)
        sha = await git_container.with_exec(["git", "rev-parse", "--short=12", "HEAD"]).stdout()

        return sha.strip()

    @function
    async def app_version(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Doc("Source code directory")],
    ) -> str:
        """Returns the app semantic version from nsv module"""
        return await dag.nsv(source).next()

    @function
    async def git_tagger(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Doc("Source code directory")],
        tag: Annotated[str, Doc("Tag for current git commit")],
        github_sa_key: Annotated[dagger.Secret, Doc("SSH key for GitHub authentication")],
    ) -> str:
        """Takes the calculated semantic version and tags the latest commit to main"""
        container = await self.git_container(source)
        return (
            await container.with_mounted_secret("/root/.ssh/id_ed25519", github_sa_key)
            .with_exec(
                [
                    "sh",
                    "-c",
                    "ssh-keyscan -t rsa,ecdsa,ed25519 github.com >> /root/.ssh/known_hosts",
                ]
            )
            .with_env_variable(
                "GIT_SSH_COMMAND",
                "ssh -i /root/.ssh/id_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes",
            )
            .with_exec(["git", "config", "user.name", "dagger-ci[bot]"])
            .with_exec(["git", "config", "user.email", "dagger@klemensgraf.com"])
            .with_exec(["git", "tag", "-f", tag])
            .with_exec(["git", "push", "origin", "--tags", "--force"])
            .stdout()
        )

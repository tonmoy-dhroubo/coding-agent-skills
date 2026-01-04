import os
from typing import List

from ..util import read_json


def detect_backend(project_root: str) -> List[str]:
    stack: List[str] = []
    if os.path.exists(os.path.join(project_root, "pom.xml")):
        stack.append("spring-boot")
    if os.path.exists(os.path.join(project_root, "build.gradle")) or os.path.exists(
        os.path.join(project_root, "build.gradle.kts")
    ):
        stack.append("gradle-java")

    package_json = os.path.join(project_root, "package.json")
    pkg = read_json(package_json) or {}
    deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})}
    if any(name.startswith("@nestjs/") for name in deps):
        stack.append("nestjs")
    if "express" in deps:
        stack.append("express")
    if "fastify" in deps:
        stack.append("fastify")

    requirements = os.path.join(project_root, "requirements.txt")
    if os.path.exists(requirements):
        text = open(requirements, "r", encoding="utf-8", errors="ignore").read()
        if "fastapi" in text:
            stack.append("fastapi")
        if "django" in text:
            stack.append("django")

    return list(dict.fromkeys(stack))

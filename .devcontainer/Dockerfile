ARG VARIANT=debian-12
FROM mcr.microsoft.com/devcontainers/base:${VARIANT}

ARG CONAN_VERSION=2.9.2
USER root

RUN find /etc/apt/sources.list* -type f -exec sed -i 's/ deb/ deb deb-src/' '{}' +

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive 

RUN apt-get -y build-dep mesa 
# Already including build-essential python3 libvulkan-dev libvulkan1 glslang-tools

RUN apt-get -y install cmake cppcheck valgrind clang lldb llvm gdb \
    vulkan-tools glslang-tools glslc libvulkan-dev libgl1-mesa-dev libgles2-mesa-dev

RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

ADD https://github.com/conan-io/conan/releases/download/${CONAN_VERSION}/conan-${CONAN_VERSION}-amd64.deb /tmp

RUN dpkg -i /tmp/conan-${CONAN_VERSION}-amd64.deb && rm -f conan-${CONAN_VERSION}-amd64.deb

USER vscode

#RUN pip install conan --break-system-packages

# [Optional] Uncomment this section to install additional packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

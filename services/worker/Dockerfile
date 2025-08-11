FROM public.ecr.aws/amazonlinux/amazonlinux:2023

# OS deps
RUN dnf -y update && dnf -y install git tar gzip unzip findutils jq curl python3-pip shadow-utils \
    java-17-amazon-corretto-devel maven gradle && dnf clean all

# non-root
RUN useradd -m app && mkdir -p /workspace && chown -R app:app /workspace
USER app
WORKDIR /home/app

# Claude Code SDK（例：Python SDK採用）※実SDK名は利用言語に合わせて置換
COPY app/requirements.txt /home/app/app/requirements.txt
RUN python3 -m pip install --user -r /home/app/app/requirements.txt

# App
COPY --chown=app:app app /home/app/app
COPY --chown=app:app entrypoint.sh /home/app/entrypoint.sh
RUN chmod +x /home/app/entrypoint.sh

ENV PATH="/home/app/.local/bin:${PATH}"
ENV WORK_DIR="/workspace"

ENTRYPOINT ["/home/app/entrypoint.sh"]
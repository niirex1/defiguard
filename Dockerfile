FROM python:3.11-slim

WORKDIR /workspace
COPY . /workspace

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -e .

# Default: regenerate paper tables/figures
CMD ["python", "-m", "defiguard.scripts.make_paper_tables_figs", "--out", "results/paper"]

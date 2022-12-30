FROM buildpack-deps:bullseye

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
        wget \
	; \
	rm -rf /var/lib/apt/lists/*

ENV CONDA_DIR /opt/conda

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

ENV PATH=$CONDA_DIR/bin:$PATH
RUN conda install -y -c anaconda python=3.8 \
    && conda config --add channels conda-forge \
    && conda install -y -c conda-forge xtb-python qcelemental ase cffi

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3"]

FROM jupyter/scipy-notebook

MAINTAINER Ivan Suftin <isuftin@usgs.gov>

# Add IOOS3 environment
USER root

# http://ioos.github.io/notebooks_demos/other_resources/
RUN wget -O environment.yml https://raw.githubusercontent.com/ioos/notebooks_demos/master/environment.yml

RUN conda config --add channels conda-forge --force

RUN conda update --yes --all && conda clean -a

RUN conda install anaconda-navigator && conda clean -a

RUN conda env create --force --file environment.yml && conda clean -a

# https://github.com/Anaconda-Platform/nb_conda_kernels
RUN conda install -c conda-forge nb_conda_kernels && conda clean -a

RUN conda create --force -n ipykernel_py3 python=3 ipykernel && conda clean -a

USER $NB_USER

CMD ["/usr/local/bin/start-singleuser.sh"]

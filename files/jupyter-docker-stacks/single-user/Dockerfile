FROM jupyter/scipy-notebook:281505737f8a

MAINTAINER Ivan Suftin <isuftin@usgs.gov>

# https://github.com/Anaconda-Platform/nb_conda_kernels
RUN conda install nb_conda_kernels && conda clean -a

RUN conda create --force -n ipykernel_py3 python=3 ipykernel && conda clean -a

# Add IOOS3 environment
# http://ioos.github.io/notebooks_demos/other_resources/
COPY ioos-environment.yml .

RUN conda env create --force --file ioos-environment.yml && conda clean -a && rm ioos-environment.yml

CMD ["/usr/local/bin/start-singleuser.sh"]

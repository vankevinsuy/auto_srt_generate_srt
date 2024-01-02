FROM python:3.11.4-slim as base_build

WORKDIR /app
RUN mkdir bucket
RUN mkdir whisper_models

#################################################
# Set environnement variable
#################################################
ENV DEBIAN_FRONTEND noninteractive
ENV MODEL_TARGET tiny

#################################################
# Install updates
#################################################
RUN apt-get update -y

#################################################
# Install basic tools
#################################################
RUN apt-get install -y \
        curl \
        git

FROM base_build as install_packages
#################################################
# install python packages
#################################################
COPY requirements.txt .
COPY install_models.py .
COPY main.py .

RUN pip install -r requirements.txt

#################################################
# Install ffmpeg
#################################################
RUN apt-get install -y --no-install-recommends ffmpeg

#################################################
# Install model
#################################################
RUN python install_models.py

CMD [ "python", "main.py" ]
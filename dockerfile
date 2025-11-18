FROM python:3.11

RUN apt update
RUN cd /tmp


# install google chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install -y ./google-chrome-stable_current_amd64.deb
RUN google-chrome --version && which google-chrome

# install chromedriver & ensure the version is compatible with the installed google chrome
RUN wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.141/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip

# move chromedriver to /usr/bin to be executable
RUN mv chromedriver-linux64/chromedriver /usr/bin/chromedriver
RUN chromedriver --version

# copy requirements and intstall packages
COPY requirements.txt /requirements.txt
RUN pip install --upgrade --no-cache-dir -r /requirements.txt
RUN rm /requirements.txt

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

FROM ubuntu:20.04

RUN apt-get update
RUN apt-get install -y software-properties-common

# FFMPEG
#The repository needs updating from the original
#Note that ffmpeg not standardly available for Ubuntu 14.04: http://www.faqforge.com/linux/how-to-install-ffmpeg-on-ubuntu-14-04/
RUN apt-get update
RUN apt-get install -y ffmpeg

# python
RUN apt-get install -y python3 python3-pip* python3-dev python3-aiofiles python3-dotenv

WORKDIR /bot-server

#COPY ./server .

#COPY ["/story-server/package.json", "./"]

RUN python3 -m pip install -U pynacl
RUN python3 -m pip install -U discord.py 

CMD [ "python3", "./bot.py" ]
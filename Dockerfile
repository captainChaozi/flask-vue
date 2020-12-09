FROM chaozi/python:base

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

ENV C_FORCE_ROOT true

ENV DISPLAY=":0" C_FORCE_ROOT=true

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime


EXPOSE 8000
CMD ["/bin/bash","docker_entry.sh"]

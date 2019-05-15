FROM images
ENV PATH /usr/lcoal/bin:$PATH
ENV LANG C.UTF-8
# 指定工作目录
ENV workspace /opt/ATFramework

# 指定端口应该和gunicorn.conf.py中定义的一致
EXPOSE 8093
COPY . $workspace

RUN set -ex \
    && cd $workspace\
    && pip install --no-cache-dir --force-reinstall -r $workspace/requirement.txt\
    && rm -rf /usr/local/python~/.cache\
    && cd $workspace
WORKDIR $workspace
CMD ['python', 'run.py']

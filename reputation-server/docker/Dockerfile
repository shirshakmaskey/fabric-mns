FROM ubuntu:bionic

RUN apt-get update \
    && apt-get install python3 -y
RUN apt-get install iputils-ping python3-pip -y \
    && apt-get install memcached libmemcached-tools -y \
    && pip3 install pylibmc python-memcached numpy pandas scipy sympy scikit-learn nose
RUN echo 'alias python="python3"' >> ~/.bashrc
CMD ["bash"]
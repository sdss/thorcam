.. highlight:: console

.. _docker:

Docker image
============

``thorcam`` can run as a Docker container in a host that is physically connected to a FLI camera. This is mainly intended for ``thorcam`` to run as part of a `thorcam <https://sdss-thorcam.readthedocs.io/en/latest/>`_.

The Dockerfile is included with the code, in the ``etc/`` directory of the repository. To build a new image, simply go to that directory and run ``make``, which is equivalent to ::

    $ docker build -f Dockerfile -t sdss5/thorcam:latest ..

(note that the context of the Docker build is the root of the ``thorcam`` repository).

Tagging and pushing
^^^^^^^^^^^^^^^^^^^

Next, tag the new image and push it to the Docker Hub ::

    $ docker tag sdss5/thorcam:latest sdss5/thorcam:<version>
    $ docker push sdss5/thorcam:<version>
    $ docker push sdss5/thorcam:latest

Note that the ``latest`` tag is consider the "default" tag to pull if you don't specify a tag version, but it's not necessarily the latest version unless you explicitely push it as such. See `this article <https://www.freecodecamp.org/news/an-introduction-to-docker-tags-9b5395636c2a/>`__ for more details.

For thorcam_ you will likely be using a private repo; make sure to also push to that repository ::

    $ docker push sdss-hub:5000/sdss5/thorcam:<version>
    $ docker push sdss-hub:5000/sdss5/thorcam:latest

Running thorcam as a container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run ``thorcam`` as a container, first make sure you have pulled the image you want to run ::

    $ docker pull sdss5/thorcam:<tag>

The run the container ::

    $ docker run --rm -d -p 19995:19995 \
                 --mount source=data,target=/data \
                 --env OBSERVATORY=$OBSERVATORY \
                 --env ACTOR_NAME=thorcam-gfa \
                 --privileged \
             sdss5/thorcam:<tag>

A few notes about this command:

- We need to run the container in detached mode (``-d``).

- We need to expose the container port that we want to use and bind it to the host port (``-p 19995:19995``). By default ``thorcam`` listens to port ``19995``. If you want to run ``thorcam`` on a different port you'll need to expose that port and change the entrypoint.

- Assuming that ``thorcam`` is going to write new images to ``/data`` we ned to create a volume and mount it in the container on that path.

- The actor name defaults to ``thorcam`` but can be changed by passing the ``ACTOR_NAME`` environment variable.

- We need to run the container in privileged mode to enable access to the host hardware in the container. It's also possible to use the ``--device`` flag, but that requires changes to the kernel configuration to ensure that the camera device is always mounted with the same name.

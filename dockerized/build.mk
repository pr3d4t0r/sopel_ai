# See:  https://raw.githubusercontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt

image:
	docker build --progress=plain --compress --force-rm -t $(DOCKER_IMAGE):$(DOCKER_VERSION) .
	docker tag $(DOCKER_IMAGE):$(DOCKER_VERSION) $(DOCKER_IMAGE):latest


push:
	docker push $(DOCKER_IMAGE):$(DOCKER_VERSION)
	docker push $(DOCKER_IMAGE):latest


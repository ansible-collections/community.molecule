COLLECTION_NAMESPACE=community
COLLECTION_NAME=molecule

ifndef PUBLISH
	PUBLISH=@echo To publish run:
else
	PUBLISH=
endif

build:
	@rm -f *.tar.gz
	@rm -rf ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME)
	ansible-galaxy collection build
	ansible-galaxy collection install -f *.tar.gz
	ansible-playbook -i hosts playbooks/validate.yml
	$(PUBLISH) ansible-galaxy collection publish *.tar.gz

test: build
	pre-commit run -a
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && ansible-test sanity

units:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && ansible-test units

integration:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && ansible-test integration

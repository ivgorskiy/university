up_local:
	docker compose -f docker-compose-local.yaml up -d

down_local:
	docker compose -f docker-compose-local.yaml down --remove-orphans

up_ci:
	docker compose -f docker-compose-ci.yaml up -d

rebuild_ci:
	docker-compose -f docker-compose-ci.yaml stop
	docker-compose -f docker-compose-ci.yaml build
	docker-compose -f docker-compose-ci.yaml up -d
	docker rmi $$(docker images -q -f dangling=true)

down_ci:
	docker compose -f docker-compose-ci.yaml down --remove-orphans

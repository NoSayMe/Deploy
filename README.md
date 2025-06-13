deploy-repo/
├── services/
│   ├── auth/
│   │   └── deploy.json
│   ├── frontend/
│   │   └── deploy.json
│   ├── payments/
│   │   └── deploy.json
│   └── ... (more services)
├── Jenkinsfile
└── README.md

## Handler service and Postgres database

The `handler` service now stores messages in a Postgres container. Two new endpoints were added:

* `POST /tools/messages` – store a message.
* `GET /tools/messages/{id}` – retrieve a stored message.

The Postgres container is defined under `services/postgres` and both services run on the same Docker network created by the Jenkins pipeline.


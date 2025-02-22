#!/bin/bash

# 创建mongo默认数据库
mongo -- "$MONGO_INITDB_DATABASE" <<EOF
    use $MONGO_INITDB_DATABASE;
    db.createUser({
        user: '$MONGO_INITDB_ROOT_USERNAME',
        pwd: '$MONGO_INITDB_ROOT_PASSWORD',
        roles: [
            {role: "root", db: "admin"},
        ]
    });
EOF

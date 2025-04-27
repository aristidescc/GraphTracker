create table nodes
(
    id          INTEGER      not null primary key,
    name        VARCHAR(100) not null unique,
    description TEXT,
    created_at  DATETIME,
    updated_at  DATETIME
);

create table edges
(
    id         INTEGER      not null primary key,
    source_id  INTEGER      not null references nodes,
    target_id  INTEGER      not null references nodes,
    name       VARCHAR(100) not null,
    weight     FLOAT,
    created_at DATETIME,
    updated_at DATETIME,
    constraint _source_target_u
        unique (source_id, target_id)
);

create table operation_logs
(
    id             INTEGER     not null primary key,
    operation_type VARCHAR(50) not null,
    details        TEXT,
    timestamp      DATETIME
);

create table visitors
(
    id              INTEGER      not null primary key,
    name            VARCHAR(100) not null,
    current_node_id INTEGER      not null references nodes,
    created_at      DATETIME,
    updated_at      DATETIME
);

create table visitor_movements
(
    id         INTEGER not null primary key,
    visitor_id INTEGER not null references visitors,
    node_id    INTEGER not null references nodes,
    edge_id    INTEGER          references edges,
    timestamp  DATETIME
);




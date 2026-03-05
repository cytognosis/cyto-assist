#!/usr/bin/env bash
# neo4j-swap-db.sh — Swap between PKG and OLS4 databases in Neo4j 5.x CE
# Usage: ./neo4j-swap-db.sh [pkg|ols4|status]

set -euo pipefail

NEO4J_HOME="${NEO4J_HOME:-/home/mohammadi/software/neo4j}"
NEO4J_DATA="$NEO4J_HOME/data"
OLS4_STORE="/home/mohammadi/datasets/ontologies/ols4/extracted_latest/databases/neo4j"

show_status() {
    if [ -L "$NEO4J_DATA/databases/neo4j" ]; then
        target=$(readlink "$NEO4J_DATA/databases/neo4j")
        echo "Current DB: OLS4 (symlink → $target)"
    elif [ -d "$NEO4J_DATA/databases/neo4j" ]; then
        echo "Current DB: PKG (direct)"
    else
        echo "No database found"
    fi
    $NEO4J_HOME/bin/neo4j status 2>/dev/null || true
}

swap_to_pkg() {
    echo "Swapping to PKG..."
    $NEO4J_HOME/bin/neo4j stop 2>/dev/null || true
    sleep 3

    if [ -L "$NEO4J_DATA/databases/neo4j" ]; then
        rm "$NEO4J_DATA/databases/neo4j"
        mv "$NEO4J_DATA/databases/pkg_backup" "$NEO4J_DATA/databases/neo4j"
    fi

    rm -rf "$NEO4J_DATA/transactions/neo4j/"*
    $NEO4J_HOME/bin/neo4j start
    echo "✅ PKG database active"
}

swap_to_ols4() {
    echo "Swapping to OLS4..."
    $NEO4J_HOME/bin/neo4j stop 2>/dev/null || true
    sleep 3

    if [ -d "$NEO4J_DATA/databases/neo4j" ] && [ ! -L "$NEO4J_DATA/databases/neo4j" ]; then
        mv "$NEO4J_DATA/databases/neo4j" "$NEO4J_DATA/databases/pkg_backup"
    fi

    ln -sf "$OLS4_STORE" "$NEO4J_DATA/databases/neo4j"
    rm -rf "$NEO4J_DATA/transactions/neo4j/"*
    $NEO4J_HOME/bin/neo4j start
    echo "✅ OLS4 database active"
}

case "${1:-status}" in
    pkg)   swap_to_pkg ;;
    ols4)  swap_to_ols4 ;;
    status) show_status ;;
    *)     echo "Usage: $0 [pkg|ols4|status]"; exit 1 ;;
esac

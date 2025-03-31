#!/usr/bin/env bash
find $PKGPATH -type f -name "$PATTERN" -exec sed -i "s/$PLCHLDR/v$STABLE/g" {} +

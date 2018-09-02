package main

import (
    "os"
    "log"
)

func extract(path string, objs chan<- string) {
    file, err := os.Open(path)
    if err != nil {
        log.Fatal(err)
    }

    objs <-
}

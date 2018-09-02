package main

import (
    "flag"
    "log"
    "path"
    "io/ioutil"
    "fmt"
)

type urlFlags []string

func (i *urlFlags) String() string {
    return ""
}

func (i *urlFlags) Set(value string) error {
    *i = append(*i, value)
    return nil
}

func makePath(dirPath string, id string) string {
    return path.Join(dirPath, id) + ".html"
}

func main() {
    var dir string
    flag.StringVar(&dir, "dir", "", "directory of downloaded HTML files")

    var langStr string
    flag.StringVar(&langStr, "lang", "", "language")

    var workerNum int
    flag.IntVar(&workerNum, "worker", 4, "number of workers")

    flag.Parse()

    lang := getLang(langStr)
    if lang == UnknownLanguage {
        log.Fatal("Unknown language: " + langStr)
    }

    files, err := ioutil.ReadDir(dir)
    if err != nil {
        log.Fatal(err)
    }

    objs := make(chan string)
    go func() {
        for obj := range objs {
            fmt.Println(obj)
        }
    }()

    for _, f := range files {
        go extract(f.Name(), objs)
    }
}

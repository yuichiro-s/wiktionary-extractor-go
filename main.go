package main

import (
    "flag"
    "log"
    "io/ioutil"
    "path"
    "os"
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
    var dump string
    flag.StringVar(&dump, "dump", "", "path to Wiktionary dump")

    var langStr string
    flag.StringVar(&langStr, "lang", "", "language")

    var urls urlFlags
    flag.Var(&urls, "url", "main URL where Wiktionary is hosted")

    var workerNum int
    flag.IntVar(&workerNum, "worker", 4, "number of workers")

    var outDir string
    flag.StringVar(&outDir, "out", "out", "output directory")

    flag.Parse()

    lang := getLang(langStr)
    if lang == UnknownLanguage {
        log.Fatal("Unknown language: " + langStr)
    }

    os.Mkdir(outDir, 0755)

    // filter out existing entries
    langEntries := readDump(dump, lang)
    newLangEntries := make(chan LangEntry)
    go func() {
        for langEntry := range langEntries {
            p := makePath(outDir, langEntry.oldid)
            if _, err := os.Stat(p); os.IsNotExist(err) {
                newLangEntries <- langEntry
            } else {
                log.Println("Already exists, skipped: " + p)
            }
        }
        close(newLangEntries)
    }()

    renderer := EntryRenderer{urls: urls, workerNum: workerNum}
    for entry := range renderer.renderEntries(newLangEntries) {
        p := makePath(outDir, entry.id)
        log.Printf("Writing to %s\n", p)
        ioutil.WriteFile(p, []byte(entry.text), 0644)
    }
}

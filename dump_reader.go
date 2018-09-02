package main

import (
    "strings"
    "os"
    "log"
    "encoding/xml"
)

type LangEntry struct {
    title      string
    oldid      string
    sectionNum int
}

func readDump(dumpPath string, lang Lang) <-chan LangEntry {
    dumpFile, err := os.Open(dumpPath)
    if err != nil {
        log.Fatal(err)
        return nil
    }
    entries := make(chan LangEntry)

    go func() {
        decoder := xml.NewDecoder(dumpFile)
        var currentId string
        var currentTitle string
        var currentText string
        var tags []string
        for {
            t, err := decoder.Token()
            if err != nil {
                log.Fatal(err)
                break
            } else if t == nil {
                break
            }
            switch e := t.(type) {
            case xml.StartElement:
                tags = append(tags, e.Name.Local)
            case xml.CharData:
                if len(tags) >= 1 {
                    lastTag := tags[len(tags)-1]
                    if lastTag == "title" {
                        currentTitle = string(e)
                    } else if len(tags) >= 2 && lastTag == "id" && tags[len(tags)-2] == "revision"{
                        currentId = string(e)
                    } else if lastTag == "text" {
                        currentText = string(e)
                    }
                }
            case xml.EndElement:
                tags = tags[:len(tags)-1]
                if e.Name.Local == "revision" {
                    sectionNum := getSectionNumber(currentText, lang)
                    if sectionNum > 0 {
                        entries <- LangEntry{title: currentTitle, oldid: currentId, sectionNum: sectionNum}
                    }
                }
            }
        }
        close(entries)
        dumpFile.Close()
    }()

    return entries
}

func getSectionNumber(text string, lang Lang) int {
    langTitle := langTitles[lang]
    sectionNum := 0
    for _, line := range strings.Split(text, "\n") {
        if strings.HasPrefix(line, "==") {
            sectionNum++
            if line == langTitle {
                return sectionNum
            }
        }
    }
    return 0
}

package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"regexp"
	"strconv"
	"sync"
)

type EntryRenderer struct {
	urls      []string
	workerNum int
}

type RenderedEntry struct {
	title string
	id    string
	text  string
}

func (r EntryRenderer) renderEntries(entries <-chan LangEntry) <-chan RenderedEntry {
	renderedEntries := make(chan RenderedEntry)

	wg := new(sync.WaitGroup)
	for w := 0; w < r.workerNum; w++ {
		wg.Add(1)
		go worker(wg, r.urls, entries, renderedEntries)
	}

	go func() {
		wg.Wait()
		close(renderedEntries)
	}()

	return renderedEntries
}

func worker(wg *sync.WaitGroup, urls []string, langEntries <-chan LangEntry, renderedEntries chan<- RenderedEntry) {
	defer wg.Done()

	client := &http.Client{}
	for langEntry := range langEntries {
		renderedEntry := render(langEntry, client, urls)
		if renderedEntry == nil {
			log.Println("Rendering failed: " + langEntry.title)
		} else {
			renderedEntries <- *renderedEntry
		}
	}
}

func render(entry LangEntry, client *http.Client, urls []string) *RenderedEntry {
	for _, url := range urls {
		renderedText, err := request(client, url, entry)
		if err != nil {
			log.Println(err)
		} else {
			return &RenderedEntry{title: entry.title, id: entry.oldid, text: *renderedText}
		}
	}
	return nil
}

var r, _ = regexp.Compile("<span.*>Lua error.*?</span>")

func request(client *http.Client, url string, entry LangEntry) (*string, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	q := req.URL.Query()
	q.Add("action", "parse")
	q.Add("format", "json")
	q.Add("oldid", entry.oldid)
	q.Add("section", strconv.Itoa(entry.sectionNum))
	q.Add("disablelimitreport", "true")
	q.Add("disableeditsection", "true")
	q.Add("disablestylededuplication", "true")
	req.URL.RawQuery = q.Encode()
	log.Printf("Connecting: %s\n", req.URL)
	res, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	bytes, err := ioutil.ReadAll(res.Body)
	str := string(bytes)
	if err != nil {
		return nil, err
	}

	if res.StatusCode != 200 {
		return nil, errors.New(fmt.Sprintf("Status not 200 OK: %d %s", res.StatusCode, str))
	}

	// decode JSON
	var body struct {
		Parse struct {
			Text map[string]string
		}
	}
	err = json.Unmarshal(bytes, &body)
	if err != nil {
		return nil, err
	}
	renderedText := body.Parse.Text["*"]

	// detect Lua error
	matches := r.FindSubmatch([]byte(renderedText))
	if len(matches) > 0 {
		return nil, errors.New("Lua error detected: " + string(matches[0]))
	}

	return &renderedText, nil
}

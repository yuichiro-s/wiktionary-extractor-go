package main

// Lang represents a language.
type Lang int

const (
	// UnknownLanguage represents that the language is unknown.
	UnknownLanguage Lang = iota
	// EnEs represents Spanish entries on English Wiktionary.
	EnEs
	// EnEn represents English entries on English Wiktionary.
	EnEn
	// EnDe represents German entries on English Wiktionary.
	EnDe
	// EnZh represents Chinese entries on English Wiktionary.
	EnZh
	// EnKo represents Korean entries on English Wiktionary.
	EnKo
	// JaKo represents Korean entries on Japanese Wiktionary.
	JaKo
)

func getLang(langStr string) Lang {
	switch langStr {
	case "en-es":
		return EnEs
	case "en-en":
		return EnEn
	case "en-de":
		return EnDe
	case "en-zh":
		return EnZh
	case "en-ko":
		return EnKo
	case "ja-ko":
		return JaKo
	default:
		return UnknownLanguage
	}
}

var langTitles = map[Lang][]string{
	EnEs: {"==Spanish=="},
	EnEn: {"==English=="},
	EnDe: {"==German=="},
	EnKo: {"==Korean=="},
	EnZh: {"==Chinese=="},
	JaKo: {"==朝鮮語==", "=={{ko}}==", "=={{kor}}==", "=={{kor-KP}}==", "=={{kor-KR}=="},
}

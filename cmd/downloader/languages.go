package main

type Lang int

const (
    UnknownLanguage Lang = iota
    EnEs
    EnEn
    EnDe
    EnKo
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
    JaKo: {"==朝鮮語==", "=={{ko}}==", "=={{kor}}==", "=={{kor-KP}}==", "=={{kor-KR}=="},
}

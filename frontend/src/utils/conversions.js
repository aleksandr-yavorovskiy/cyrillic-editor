function convertText(text, fromDict, toDict) {
  let result = ""

  for (let char of text) {
    let unicodeChar = char

    if (fromDict && char in fromDict.FontToUnicode) {
      unicodeChar = fromDict.FontToUnicode[char]
    }

    if (toDict && unicodeChar in toDict.UnicodeToFont) {
      result += toDict.UnicodeToFont[unicodeChar]
    } else {
      result += unicodeChar
    }
  }

  return result
}

function convertDirect(text, mapping) {
  let result = ""
  for (let char of text) {
    result += (char in mapping) ? mapping[char] : char
  }
  return result
}

export { convertText, convertDirect }

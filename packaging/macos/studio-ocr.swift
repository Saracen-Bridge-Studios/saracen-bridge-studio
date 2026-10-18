// Saracen Bridge Studio's OCR on the Mac (1.2): Apple's own text recognition (the Vision framework, built into
// macOS), so the Mac build needs no Tesseract. It answers like `tesseract <image> stdout ... tsv`: word boxes in
// Tesseract's TSV columns, which studio.ocr.tsv_to_lines turns into screenplay-shaped lines. Arguments after the
// image are accepted and ignored, so studio.ocr calls it exactly as it calls Tesseract.
//
// Build (on a Mac): swiftc -O -o studio-ocr studio-ocr.swift
import Foundation
import ImageIO
import Vision

func fail(_ msg: String, _ code: Int32 = 1) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(code)
}

let args = CommandLine.arguments
if args.count < 2 { fail("usage: studio-ocr <image> [stdout ...]", 2) }
guard let source = CGImageSourceCreateWithURL(URL(fileURLWithPath: args[1]) as CFURL, nil),
      let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else { fail("Can't read the page image.") }
let W = Double(image.width), H = Double(image.height)

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = ["en-US"]
request.usesLanguageCorrection = true
do { try VNImageRequestHandler(cgImage: image, options: [:]).perform([request]) } catch { fail("OCR failed: \(error)") }

struct Word { let left: Int, top: Int, width: Int, height: Int, conf: Int; let text: String }
struct Line { var center: Double; var height: Double; var words: [Word] }

func pixels(_ r: CGRect) -> (Int, Int, Int, Int) {        // Vision boxes are 0-1 with the origin bottom-left
    (Int((r.minX * W).rounded()), Int(((1 - r.maxY) * H).rounded()), Int((r.width * W).rounded()), Int((r.height * H).rounded()))
}

var lines: [Line] = []
for observation in request.results ?? [] {
    guard let best = observation.topCandidates(1).first else { continue }
    let s = best.string
    var words: [Word] = []
    var i = s.startIndex
    while i < s.endIndex {
        while i < s.endIndex && s[i].isWhitespace { i = s.index(after: i) }
        if i >= s.endIndex { break }
        var j = i
        while j < s.endIndex && !s[j].isWhitespace { j = s.index(after: j) }
        let box = (try? best.boundingBox(for: i..<j))?.boundingBox ?? observation.boundingBox
        let (l, t, w, h) = pixels(box)
        words.append(Word(left: l, top: t, width: w, height: h, conf: Int(best.confidence * 100), text: String(s[i..<j])))
        i = j
    }
    if words.isEmpty { continue }
    // Vision may read one printed line as several pieces (a scene number far from its heading): pieces whose
    // middles sit within half a line of each other are one line, as Tesseract reports them.
    let (_, t, _, h) = pixels(observation.boundingBox)
    let center = Double(t) + Double(h) / 2
    if let k = lines.firstIndex(where: { abs($0.center - center) < max($0.height, Double(h)) / 2 }) {
        lines[k].words += words
    } else {
        lines.append(Line(center: center, height: Double(h), words: words))
    }
}
lines.sort { $0.center < $1.center }

var out = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
for (n, line) in lines.enumerated() {
    for (k, w) in line.words.sorted(by: { $0.left < $1.left }).enumerated() {
        out += "5\t1\t1\t1\t\(n + 1)\t\(k + 1)\t\(w.left)\t\(w.top)\t\(w.width)\t\(w.height)\t\(w.conf)\t\(w.text)\n"
    }
}
FileHandle.standardOutput.write(out.data(using: .utf8)!)

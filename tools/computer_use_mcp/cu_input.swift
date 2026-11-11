// Compiled lazily by server.py. No UI automation libraries or permission prompts.
import AppKit
import ApplicationServices
import CoreGraphics
import Foundation

enum InputError: Error, CustomStringConvertible {
    case message(String)
    var description: String {
        switch self { case .message(let text): return text }
    }
}

func fail(_ message: String) throws -> Never { throw InputError.message(message) }

func emit(_ value: [String: Any]) throws {
    let data = try JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write(Data([10]))
}

func number(_ args: [String: Any], _ key: String, default fallback: Double? = nil) throws -> Double {
    if args[key] == nil, let fallback = fallback { return fallback }
    guard let value = args[key] as? NSNumber, value.doubleValue.isFinite else {
        try fail("Missing or invalid numeric argument")
    }
    return value.doubleValue
}

func point(_ args: [String: Any], _ x: String, _ y: String) throws -> CGPoint {
    let p = CGPoint(x: try number(args, x), y: try number(args, y))
    var count: UInt32 = 0
    guard CGGetDisplaysWithPoint(p, 0, nil, &count) == .success, count > 0 else {
        try fail("Coordinates are outside active displays; use screenshot mapping to screen points")
    }
    return p
}

func mouse(_ type: CGEventType, _ point: CGPoint, _ button: CGMouseButton,
           clickState: Int64 = 1) throws {
    guard let event = CGEvent(mouseEventSource: nil, mouseType: type,
                              mouseCursorPosition: point, mouseButton: button) else {
        try fail("Cannot create mouse event")
    }
    event.setIntegerValueField(.mouseEventClickState, value: clickState)
    event.post(tap: .cghidEventTap)
}

// CGWindowList is ordered front to back in Quartz screen-point coordinates.
// Keep system windows in the list: excluding them would click through the Dock
// or a status item into an otherwise allowed app window underneath.
func windowAtPoint(_ p: CGPoint) throws -> [String: Any] {
    guard let windows = CGWindowListCopyWindowInfo(.optionOnScreenOnly, kCGNullWindowID)
            as? [[String: Any]] else { try fail("Cannot inspect window ownership") }
    for window in windows {
        guard let rawBounds = window[kCGWindowBounds as String] as? [String: Any],
              let bounds = CGRect(dictionaryRepresentation: rawBounds as CFDictionary),
              let alpha = window[kCGWindowAlpha as String] as? NSNumber else {
            try fail("Cannot inspect window bounds/visibility")
        }
        if alpha.doubleValue <= 0 || !bounds.contains(p) { continue }
        guard let pid = window[kCGWindowOwnerPID as String] as? NSNumber,
              let layer = window[kCGWindowLayer as String] as? NSNumber,
              let app = NSRunningApplication(processIdentifier: pid.int32Value),
              let bundle = app.bundleIdentifier else { try fail("Cannot inspect window owner") }
        return ["pid": pid.int32Value, "bundle_id": bundle, "layer": layer.intValue]
    }
    try fail("Click refusal: no owning window at target point")
}

func checkClickTarget(_ args: [String: Any], _ p: CGPoint) throws {
    guard let expectedPID = args["expected_pid"] as? NSNumber,
          let expectedBundle = args["expected_bundle_id"] as? String,
          let frontmost = NSWorkspace.shared.frontmostApplication,
          frontmost.processIdentifier == expectedPID.int32Value,
          frontmost.bundleIdentifier == expectedBundle else {
        try fail("Click refusal: frontmost app changed")
    }
    let target = try windowAtPoint(p)
    guard target["pid"] as? Int32 == expectedPID.int32Value,
          target["bundle_id"] as? String == expectedBundle,
          target["layer"] as? Int == 0, expectedBundle != "com.apple.dock" else {
        try fail("Click refusal: target is outside the allowed app window (Dock/status items refused)")
    }
}

// ANSI virtual keys. Named navigation/function keys are layout independent;
// character shortcuts use their physical ANSI positions. Unicode text uses UTF-16.
let keyCodes: [String: CGKeyCode] = [
    "a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7,
    "c": 8, "v": 9, "b": 11, "q": 12, "w": 13, "e": 14, "r": 15,
    "y": 16, "t": 17, "1": 18, "2": 19, "3": 20, "4": 21, "6": 22,
    "5": 23, "=": 24, "9": 25, "7": 26, "-": 27, "8": 28, "0": 29,
    "]": 30, "o": 31, "u": 32, "[": 33, "i": 34, "p": 35,
    "return": 36, "enter": 36, "l": 37, "j": 38, "'": 39, "k": 40,
    ";": 41, "\\": 42, ",": 43, "/": 44, "n": 45, "m": 46, ".": 47,
    "tab": 48, "space": 49, "backtick": 50, "delete": 51, "backspace": 51,
    "escape": 53, "esc": 53, "f17": 64, "f18": 79, "f19": 80,
    "f20": 90, "f5": 96, "f6": 97, "f7": 98, "f3": 99, "f8": 100,
    "f9": 101, "f11": 103, "f13": 105, "f16": 106, "f14": 107,
    "f10": 109, "f12": 111, "f15": 113, "home": 115, "pageup": 116,
    "forwarddelete": 117, "f4": 118, "end": 119, "f2": 120,
    "pagedown": 121, "f1": 122, "left": 123, "right": 124, "down": 125, "up": 126
]

func pressKey(_ combo: String) throws {
    let parts = combo.lowercased().split(separator: "+", omittingEmptySubsequences: false)
        .map { String($0).trimmingCharacters(in: .whitespaces) }
    guard let last = parts.last, let code = keyCodes[last] else {
        try fail("Unsupported key; use a named key/ANSI character (type_text for Unicode)")
    }
    var flags: CGEventFlags = []
    for modifier in parts.dropLast() {
        switch modifier {
        case "cmd", "command": flags.insert(.maskCommand)
        case "ctrl", "control": flags.insert(.maskControl)
        case "alt", "option", "opt": flags.insert(.maskAlternate)
        case "shift": flags.insert(.maskShift)
        case "fn": flags.insert(.maskSecondaryFn)
        default: try fail("Unsupported key modifier")
        }
    }
    // Repeat the Python guard at the posting boundary, including modifier aliases.
    if (flags.contains(.maskCommand) && ["tab", "space"].contains(last)) ||
       (flags.contains(.maskControl) && ["up", "down"].contains(last)) ||
       (flags.contains(.maskCommand) && flags.contains(.maskAlternate) && ["esc", "escape"].contains(last)) {
        try fail("App-switching and launcher key combos are blocked")
    }
    guard let down = CGEvent(keyboardEventSource: nil, virtualKey: code, keyDown: true),
          let up = CGEvent(keyboardEventSource: nil, virtualKey: code, keyDown: false) else {
        try fail("Cannot create keyboard event")
    }
    down.flags = flags
    up.flags = flags
    down.post(tap: .cghidEventTap)
    up.post(tap: .cghidEventTap)
}

func typeText(_ text: String) throws {
    let units = Array(text.utf16)
    var start = 0
    while start < units.count {
        var end = min(start + 20, units.count)
        // Never split a supplementary Unicode character's surrogate pair.
        if end < units.count && (0xD800...0xDBFF).contains(units[end - 1]) { end += 1 }
        let chunk = Array(units[start..<end])
        guard let down = CGEvent(keyboardEventSource: nil, virtualKey: 0, keyDown: true),
              let up = CGEvent(keyboardEventSource: nil, virtualKey: 0, keyDown: false) else {
            try fail("Cannot create Unicode keyboard event")
        }
        chunk.withUnsafeBufferPointer { buffer in
            down.keyboardSetUnicodeString(stringLength: chunk.count, unicodeString: buffer.baseAddress!)
            up.keyboardSetUnicodeString(stringLength: chunk.count, unicodeString: buffer.baseAddress!)
        }
        down.post(tap: .cghidEventTap)
        up.post(tap: .cghidEventTap)
        start = end
    }
}

func run() throws {
    guard CommandLine.arguments.count == 2 else { try fail("Expected one helper operation") }
    let operation = CommandLine.arguments[1]
    let data = FileHandle.standardInput.readDataToEndOfFile()
    guard let args = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
        try fail("Expected JSON object on stdin")
    }
    switch operation {
    case "permissions_status":
        try emit(["screen_recording": CGPreflightScreenCaptureAccess(),
                  "accessibility": AXIsProcessTrusted()])
        return
    case "frontmost_app":
        guard let app = NSWorkspace.shared.frontmostApplication, let name = app.localizedName else {
            try fail("Cannot determine frontmost app")
        }
        try emit(["name": name, "bundle_id": app.bundleIdentifier ?? "", "pid": app.processIdentifier])
        return
    case "window_at_point":
        try emit(windowAtPoint(point(args, "x", "y")))
        return
    case "display_info":
        let display = CGMainDisplayID()
        let bounds = CGDisplayBounds(display)
        try emit(["x": bounds.origin.x, "y": bounds.origin.y,
                  "width": bounds.width, "height": bounds.height,
                  "pixel_width": CGDisplayPixelsWide(display), "pixel_height": CGDisplayPixelsHigh(display)])
        return
    default: break
    }
    guard AXIsProcessTrusted() else { try fail("Accessibility permission is missing") }
    switch operation {
    case "move":
        try mouse(.mouseMoved, point(args, "x", "y"), .left)
    case "click":
        let p = try point(args, "x", "y")
        let name = args["button"] as? String ?? "left"
        guard ["left", "right"].contains(name) else { try fail("Invalid mouse button") }
        let count = try number(args, "count", default: 1)
        guard count == 1 || count == 2 else { try fail("Click count must be 1 or 2") }
        let right = name == "right"
        let button: CGMouseButton = right ? .right : .left
        try checkClickTarget(args, p)
        try mouse(.mouseMoved, p, button)
        for i in 1...Int(count) {
            try checkClickTarget(args, p)
            try mouse(right ? .rightMouseDown : .leftMouseDown, p, button, clickState: Int64(i))
            try mouse(right ? .rightMouseUp : .leftMouseUp, p, button, clickState: Int64(i))
            if i < Int(count) { Thread.sleep(forTimeInterval: 0.08) }
        }
    case "drag":
        let from = try point(args, "x", "y"), to = try point(args, "to_x", "to_y")
        let duration = try number(args, "duration", default: 0.5)
        guard duration >= 0.1 && duration <= 5 else { try fail("Drag duration outside 0.1...5 seconds") }
        try mouse(.mouseMoved, from, .left)
        try mouse(.leftMouseDown, from, .left)
        // Release the button even if creation of an intermediate event fails.
        defer { try? mouse(.leftMouseUp, to, .left) }
        let steps = max(2, Int(duration * 60))
        for i in 1...steps {
            let t = Double(i) / Double(steps)
            let p = CGPoint(x: from.x + (to.x - from.x) * t, y: from.y + (to.y - from.y) * t)
            try mouse(.leftMouseDragged, p, .left)
            Thread.sleep(forTimeInterval: duration / Double(steps))
        }
    case "scroll":
        let dx = try number(args, "dx", default: 0), dy = try number(args, "dy")
        guard abs(dx) <= 5000 && abs(dy) <= 5000,
              dx.rounded() == dx && dy.rounded() == dy else { try fail("Scroll deltas must be integers within +/-5000") }
        guard let event = CGEvent(scrollWheelEvent2Source: nil, units: .pixel, wheelCount: 2,
                                  wheel1: Int32(dy), wheel2: Int32(dx), wheel3: 0) else {
            try fail("Cannot create scroll event")
        }
        event.post(tap: .cghidEventTap)
    case "key":
        guard let combo = args["combo"] as? String else { try fail("Missing key combo") }
        try pressKey(combo)
    case "type_text":
        guard let text = args["text"] as? String, text.count <= 10000 else { try fail("Invalid text") }
        try typeText(text)
    default: try fail("Unknown helper operation")
    }
    try emit(["ok": true])
}

do { try run() }
catch {
    FileHandle.standardError.write(Data(("cu_input: \(error)\n").utf8))
    exit(1)
}

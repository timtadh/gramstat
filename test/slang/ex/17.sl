
        var f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
        var g = func(h) { return h() }
        print g(f)
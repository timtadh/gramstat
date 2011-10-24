
        var g = func() {
            var g1 = func() { return g2() }
            var g2 = func() { return g3() }
            var g3 = func() { return h() }
            return g1()
        }
        var h = func() { return f() }
        var f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
        print g()

        var sub = func(a, b) {
            var c = 0
            var _sub = func() {
                c = a - b
                return
            }
            _sub()
            return c
        }
        var call = func(f, a, b) {
            return f(a, b)
        }
        print call(sub, 5+7, 8)
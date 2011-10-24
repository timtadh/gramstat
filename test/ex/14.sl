
        var sub = func(a, b) {
            var c = 0
            var _sub = func() {
                c = a - b
                return
            }
            _sub()
            return c
        }
        print sub(5+7, 8)
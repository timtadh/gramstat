
        var sub = func(a, b) {
            var _sub = func() {
                return a - b
            }
            return _sub()
        }
        print sub(5+7, 8)
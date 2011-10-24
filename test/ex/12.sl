
        var sub = func(a, b) {
            var c = 0
            var _sub = func() {
                c = 1 // modifies upper c.
                var c = a - b // creates a new c.
                print c
                // var c = 5 // causes type error do to var redeclare in same scope
                print c
                return
            }
            _sub()
            return c
        }
        var call = func(f, a, b) {
            return f(a, b)
        }
        print call(sub, 5+7, 8)
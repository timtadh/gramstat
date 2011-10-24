f = func(x) {
            if (x > 0) {
                if (x/2 + x/2 == x) { // then it is even
                    c = f(x+1)
                } else {
                    c = f(x-3)
                }
            } else {
                if (x < 5) {
                    if (x != 0) {
                        x = x - 1
                    }
                    c = x
                } else {
                    c = 10
                }
            }
            return c
        }
        print f(10)
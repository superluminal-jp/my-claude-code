workspace "<System name>" "Architecture model of <system name>; views are generated from this one model." {

    model {
        member = person "<Role name>" "<What they do with the system>"
        external1 = softwareSystem "<External system>" "<What it does for this system>" "External"

        sys = softwareSystem "<System name>" "<What it is responsible for>" {
            web = container "<Web app>" "<What it shows the user>" "<technology>"
            api = container "<API>" "<What it accepts and decides>" "<technology>"
            db = container "<Database>" "<What it stores>" "<technology>" "Database"
        }

        member -> web "<What they ask for and why>" "HTTPS"
        web -> api "<What it sends and why>" "JSON/HTTPS"
        api -> db "<What it reads and writes>" "SQL/TLS"
        api -> external1 "<What it asks for and why>" "<protocol>"
    }

    views {
        systemContext sys "context" "System context view: <system name>" {
            include *
            autoLayout lr
        }

        container sys "containers" "Container view: <system name>" {
            include *
            autoLayout lr
        }

        styles {
            element "Person" {
                shape Person
                background #CFE0F3
                stroke #1F4E79
                color #0B1F33
            }
            element "Software System" {
                background #DCE9F7
                stroke #1F4E79
                color #0B1F33
            }
            element "Container" {
                background #E8F1FB
                stroke #1F4E79
                color #0B1F33
            }
            element "Database" {
                shape Cylinder
            }
            element "External" {
                background #EDEDED
                stroke #4D4D4D
                border dashed
                color #0B1F33
            }
        }
    }
}

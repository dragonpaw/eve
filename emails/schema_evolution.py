
# all of your evolution scripts, mapping the from_version and to_version to a list if sql commands
mysql_evolutions = [
    [('fv1:5462587177660420601','fv1:-6386810879993049206'), # generated 2009-09-09 01:39:58.277481
        "CREATE TABLE `emails_message` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `profile_id` integer NOT NULL,\n    `body` longtext NOT NULL,\n    `subject` varchar(100) NOT NULL,\n    `date` datetime NOT NULL,\n    `order` integer,\n    `from_address` varchar(75) NOT NULL,\n    `to_address` varchar(75) NOT NULL\n)\n;",
    ],
] # don't delete this comment! ## mysql_evolutions_end ##

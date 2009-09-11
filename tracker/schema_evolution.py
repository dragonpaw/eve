
# all of your evolution scripts, mapping the from_version and to_version to a list if sql commands
mysql_evolutions = [
    [('fv1:-465050077665312265','fv1:-1843084956313736917'), # generated 2009-09-09 01:39:43.565408
        "CREATE TABLE `tracker_ticket` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `title` varchar(100) NOT NULL,\n    `project` varchar(100) NOT NULL,\n    `submitted_date` date NOT NULL,\n    `modified_date` date NOT NULL,\n    `submitter_id` integer NOT NULL,\n    `assigned_to_id` integer NOT NULL,\n    `description` longtext NOT NULL,\n    `status` integer NOT NULL,\n    `priority` integer NOT NULL\n)\n;",
        "CREATE TABLE `tracker_changelog` (\n    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,\n    `date` datetime NOT NULL,\n    `description` longtext NOT NULL\n)\n;",
    ],
] # don't delete this comment! ## mysql_evolutions_end ##

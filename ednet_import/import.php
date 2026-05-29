<?php

require('../../config.php');
require_login();

global $DB;

set_time_limit(0);
ini_set('memory_limit', '512M');

$file = __DIR__ . '/data/kt1_merged_sample_part2.csv';

if (!file_exists($file)) {
    die(" File not found");
}

echo " File found<br>";

$handle = fopen($file, "r");

if (!$handle) {
    die("Cannot open file");
}

echo " File opened<br>";

/*
 * SKIP HEADER
 */
fgets($handle);

echo "Header skipped<br><br>";

/*
 * DELETE OLD DATA
 */
$DB->delete_records('local_ednet_interactions');

echo " Old data deleted<br><br>";

$count = 0;

while (($line = fgets($handle)) !== false) {

    $data = str_getcsv($line, ',', '"');

    /*
     * CHECK COLUMN COUNT
     */
    if (count($data) < 12) {
        continue;
    }

    /*
     * DEBUG SAMPLE
     */
    if ($count == 0) {
        echo " Sample row:<br><pre>";
        print_r($data);
        echo "</pre><br>";
    }

    $record = new stdClass();

    /*
     * RAW DATA
     */

    // timestamp
    $record->timestamp = trim($data[0]);

    // q356
    $record->question_id = trim($data[2]);

    // user answer
    $record->user_answer = trim($data[3]);

    // elapsed time ms
    $record->elapsed_time = (int)$data[4];

    // u1
    $record->user_id = trim($data[5]);

    // correct answer
    $record->correct_answer = trim($data[7]);

    /*
     * INSERT
     */
    $DB->insert_record(
        'local_ednet_interactions',
        $record
    );

    $count++;

    /*
     * PROGRESS
     */
    if ($count % 5000 == 0) {

        echo "Inserted: $count<br>";

        ob_flush();
        flush();
    }
}

fclose($handle);

echo "<br> DONE: Imported $count records<br>";

/*
 * TEST
 */
echo "<h3> Test data:</h3>";

$test = $DB->get_records(
    'local_ednet_interactions',
    null,
    '',
    '*',
    0,
    5
);

foreach ($test as $t) {

    echo
        "$t->user_id | " .
        "$t->question_id | " .
        "$t->user_answer | " .
        "$t->correct_answer | " .
        "$t->elapsed_time<br>";
}

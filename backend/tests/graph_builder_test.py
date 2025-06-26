from app.chat.similarity_computer import return_similarity_matches
from app.chat.graph_builder import draw_graph, build_similarity_graph



req_json_test = [
    {
        "id": "US1-M1",
        "description": "There is a login and authorization system for the role of 'report manager’ whenever a user logs into the web service.",
        "type": "Functional",
        "priority": "Must"
    },
    {
        "id": "US2-M1",
        "description": "The API must be able to retrieve the questionnaire from the database.",
        "type": "Functional",
        "priority": "Must"
    },
    {
        "id": "US2-M2",
        "description": "The API must be able to create the report with responses in the database.",
        "type": "Functional",
        "priority": "Must"
    },
    {
        "id": "US2-M3",
        "description": "The reporter must be able to fill in the questionnaire, and submit it.",
        "type": "Functional",
        "priority": "Must"
    },
    {
        "id": "US2-M4",
        "description": "The API must be able to create answers in the database to answer open questions.",
        "type": "Functional",
        "priority": "Must"
    },
    {
        "id": "US2-S5",
        "description": "Reporters should be able to optionally add files they want to include in their submission.",
        "type": "Non-functional",
        "priority": "Should"
    },
    {
        "id": "US2-S6",
        "description": "The system should allow email notification when the status of the report is marked as ‘resolved’.",
        "type": "Non-functional",
        "priority": "Should"
    },
    {
        "id": "US6-S1",
        "description": "A ‘report manager’ should be able to assign themselves to a report.",
        "type": "Functional",
        "priority": "Should"
    },
    {
        "id": "US6-S2",
        "description": "The API must be able to update report entries in the database to assign ‘report manager’ to the report.",
        "type": "Functional",
        "priority": "Should"
    },
    {
        "id": "US6-S3",
        "description": "Reports must have an assigned maintainer field.",
        "type": "Functional",
        "priority": "Must"
    },
    {
        "id": "US7-M1",
        "description": "The questionnaire has a question asking for the email address of the reporter.",
        "type": "Functional",
        "priority": "Must"
    },
    {
        "id": "US7-S2",
        "description": "The questionnaire has a question asking to allow email notification when the status of the report is marked as ‘resolved’.",
        "type": "Non-functional",
        "priority": "Should"
    },
    {
        "id": "US7-S3",
        "description": "The system should send an email notification to the reporter when a ‘report manager’ sets the status of the report as resolved.",
        "type": "Non-functional",
        "priority": "Should"
    },
    {
        "id": "US8-S1",
        "description": "A ‘report manager’ should have a dashboard with statistics on how many malfunctions have been fixed over a set timeframe.",
        "type": "Functional",
        "priority": "Should"
    },
    {
        "id": "US9-C1",
        "description": "The API must be able to store pre-filled reports.",
        "type": "Functional",
        "priority": "Want"
    },
    {
        "id": "US9-C2",
        "description": "The pre-filled reports could be accessible through a URL.",
        "type": "Functional",
        "priority": "Want"
    },
    {
        "id": "US9-C3",
        "description": "The pre-filled report’s URL can be converted to a QR code within the application.",
        "type": "Non-functional",
        "priority": "Want"
    },
    {
        "id": "US10-C1",
        "description": "The API could be able to access the pre-filled reports.",
        "type": "Functional",
        "priority": "Want"
    },
    {
        "id": "US10-C2",
        "description": "The pre-filled reports could be accessible through a URL.",
        "type": "Functional",
        "priority": "Want"
    },
    {
        "id": "US10-C3",
        "description": "When using the URL to open the pre-filled report, it allows reporters to enter data and submit their report as a normal report submission.",
        "type": "Functional",
        "priority": "Want"
    },
    {
        "id": "US11-M1",
        "description": "The backend must be developed with the PHP framework Laravel.",
        "type": "Non-functional",
        "priority": "Must"
    },
    {
        "id": "US11-M2",
        "description": "The frontend must be developed with the JS framework React.",
        "type": "Non-functional",
        "priority": "Must"
    },
    {
        "id": "US11-M3",
        "description": "The API must adhere to the RESTful principles.",
        "type": "Non-functional",
        "priority": "Must"
    },
    {
        "id": "US11-S4",
        "description": "The system should use MySQL as the database.",
        "type": "Non-functional",
        "priority": "Should"
    },
    {
        "id": "US11-S5",
        "description": "The system should have a responsive design for mobile devices.",
        "type": "Non-functional",
        "priority": "Must"
    },
    {
        "id": "US11-S6",
        "description": "The system should be scalable to handle increased load and new features.",
        "type": "Non-functional",
        "priority": "Must"
    }
]

func_json_test = [{'type': 'method_declaration', 'name': 'createApplication', 'code': "public function createApplication(): Application\n    {\n        $app = require __DIR__.'/../bootstrap/app.php';\n\n        $app->make(Kernel::class)->bootstrap();\n        return $app;\n    }", 'start_line': 13, 'end_line': 19, 'comment': '/**\n     * Creates the application.\n     */', 'file': '../../code_repos/raw/MRS/backend/tests/CreatesApplication.php', 'language': 'php'}, {'type': 'method_declaration', 'name': 'test_create_answer_with_valid_playload', 'code': 'public function test_create_answer_with_valid_playload(): void\n    {\n        $answer_payload = [\n            "answer" => "Test answer1"\n        ];\n\n        $request = $this->json(\'post\', \'/api/answers\', $answer_payload);\n        $request->assertStatus(200);\n        $this->assertDatabaseHas(\'answers\', $answer_payload);\n        $this->assertDatabaseCount(\'answers\', 1);\n    }', 'start_line': 17, 'end_line': 27, 'comment': '/**\n     * FT-AE1\n     * Test for creating an answer with valid payload\n     */', 'file': '../../code_repos/raw/MRS/backend/tests/Feature/AnswersTest.php', 'language': 'php'}, {'type': 'method_declaration', 'name': 'test_create_answer_with_invalid_payload', 'code': 'public function test_create_answer_with_invalid_payload(): void\n    {\n        // the post answer request reqires a \'answer\' key to be not null.\n        $malformed_answer_payload = [\n            "bad_payload"=>"bad"\n            // is missing answers field\n        ];\n\n        $request = $this->json(\'post\', \'/api/answers\', $malformed_answer_payload);\n        $request->assertStatus(422);\n        $this->assertDatabaseCount(\'answers\', 0);\n    }', 'start_line': 33, 'end_line': 44, 'comment': "/**\n     * FT-AE2\n     * Test for creating an answer with invalid payload\n     */\n// the post answer request reqires a 'answer' key to be not null.\n// is missing answers field", 'file': '../../code_repos/raw/MRS/backend/tests/Feature/AnswersTest.php', 'language': 'php'}, {'type': 'method_declaration', 'name': 'test_users_can_authenticate_using_the_login_endpoint', 'code': 'public function test_users_can_authenticate_using_the_login_endpoint(): void {\n        $user = User::factory()->create();\n\n        $response = $this->json(\'POST\', "/api/login", [\n            \'email\' => $user->email,\n            \'password\' => \'password\',\n        ]);\n        $response->assertStatus(200);\n    }', 'start_line': 18, 'end_line': 26, 'comment': '/**\n     * FT-AUTH1\n     * Test to check if user can login.\n     */', 'file': '../../code_repos/raw/MRS/backend/tests/Feature/AuthenticationTest.php', 'language': 'php'}, {'type': 'method_declaration', 'name': 'test_users_can_not_authenticate_with_invalid_password', 'code': 'public function test_users_can_not_authenticate_with_invalid_password(): void {\n        $user = User::factory()->create();\n\n        $response = $this->json(\'POST\', "/api/login", [\n            \'email\' => $user->email,\n            \'password\' => \'wrong-password\',\n        ]);\n\n        $response->assertUnauthorized();\n    }', 'start_line': 32, 'end_line': 41, 'comment': '/**\n     * FT-AUTH2\n     * Test to check if user is unautherized when loggin in with invalid password.\n     */', 'file': '../../code_repos/raw/MRS/backend/tests/Feature/AuthenticationTest.php', 'language': 'php'}]
print("[----------------------NAME--------------------------]")
similarity_matches = return_similarity_matches(req_json_test, func_json_test, 1, False, False)
print(similarity_matches)
print("[----------------------NAME + COMMENT------------------------]")
similarity_matches = return_similarity_matches(req_json_test, func_json_test, 1, False, True)
print(similarity_matches)
print("[----------------------NAME + COMMENT + CODE------------------------]")
similarity_matches = return_similarity_matches(req_json_test, func_json_test, 1, True, True)
print(similarity_matches)
#graph = build_similarity_graph(req_json_test, func_json_test, similarity_matches)
#draw_graph(graph)

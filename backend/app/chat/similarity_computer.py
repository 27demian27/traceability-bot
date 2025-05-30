from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def return_similarity_matches(req_json, func_json, top_n = 3, include_code: bool = False):

    req_texts, req_labels = extract_text_from_requirements(req_json)
    func_texts, func_labels = extract_text_from_functions(func_json, include_code=include_code)

    req_embeds = get_embeddings(req_texts)
    func_embeds = get_embeddings(func_texts)

    similarities = cosine_similarity(req_embeds, func_embeds)

    matches = []
    for i, req_label in enumerate(req_labels):
        ranked = sorted(
            [(func_labels[j], similarities[i][j]) for j in range(len(func_labels))],
            key=lambda x: x[1], reverse=True
        )
        matches.append((req_label, ranked[:top_n]))
    return matches

def extract_text_from_requirements(req_json):
    texts = []
    labels = []
    for req in req_json:
        description = req.get("description", "")
        req_id = req.get("id", "")
        texts.append(description)
        labels.append(req_id)
    return texts, labels

def extract_text_from_functions(func_json, include_code):
    texts = []
    labels = []
    for func in func_json:
        text = func.get('name', '')
        if include_code:
            text  = text + func.get('code', '')
        texts.append(text)
        labels.append(func.get('name', ''))
    return texts, labels

def get_embeddings(texts):
    if isinstance(texts, str):
        texts = [texts]
    return model.encode(texts)
"""
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

func_json_test = {
	"code_functions": [
		{
			"type": "method_declaration",
			"name": "test_get_report_invalid_id",
			"code": "public function test_get_report_invalid_id(): void {\n        Sanctum::actingAs(User::factory()->create());\n        $response = $this->get('/api/reports/1');\n        $response->assertStatus(404);\n    }",
			"start_line": 25,
			"end_line": 29,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_get_report",
			"code": "public function test_get_report(): void {\n        Sanctum::actingAs(User::factory()->create());\n        $report_body = [\n            'description'=>\"This is a test report\",\n            'priority'=>1,\n            'status'=>0,\n            'submitter_email'=>\"test@testing.nl\"\n        ];\n        $report = Report::create($report_body);\n        $this->assertDatabaseCount('reports', 1);\n\n        $response = $this->get('/api/reports/'.$report->id);\n        $response->assertStatus(200);\n        $response->assertSee($report_body);\n    }",
			"start_line": 35,
			"end_line": 49,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_get_reports_on_empty_database",
			"code": "public function test_get_reports_on_empty_database(): void {\n        Sanctum::actingAs(User::factory()->create());\n        $response = $this->get('/api/reports');\n        $response->assertStatus(200);\n        $response->assertSee('data');\n\n        Report::create([\n            'description'=>\"This is a test report\",\n            'priority'=>1,\n            'status'=>0,\n            'submitter_email'=>\"test@testing.nl\",\n            'responses'=>[]\n        ]);\n\n        $response = $this->get('/api/reports');\n        $response->assertStatus(200);\n        $response->assertJsonStructure([]);\n    }",
			"start_line": 55,
			"end_line": 72,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_get_reports_on_populated_database",
			"code": "public function test_get_reports_on_populated_database(): void {\n        Sanctum::actingAs(User::factory()->create());\n\n        $report = Report::create([\n            'description'=>\"This is a test report\",\n            'priority'=>0,\n            'status'=>0,\n            'submitter_email'=>\"test@testing.nl\",\n            'responses'=>[]\n        ]);\n\n        $response = $this->get('/api/reports');\n        $response->assertStatus(200);\n        $response->assertSee($report->id);\n        $response->assertSee($report->description);\n        $response->assertSee($report->submitter_email);\n    }",
			"start_line": 78,
			"end_line": 94,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_create_report_invalid_payload",
			"code": "public function test_create_report_invalid_payload(): void {\n\n        $malformed_report_payload = [\n            'malformed'=>\"This is a malformed payload\"\n            // is missing a discription\n        ];\n\n        $request = $this->json('post', '/api/reports', $malformed_report_payload);\n        $request->assertStatus(422);\n        $this->assertDatabaseCount('reports', 0);\n    }",
			"start_line": 100,
			"end_line": 110,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_create_report_invalid_email",
			"code": "public function test_create_report_invalid_email(): void {\n        $malformed_report_payload = [\n            'description'=>\"This is a malformed payload\",\n            'submitter_email'=>\"not an email address\",\n        ];\n\n        $request = $this->json('post', '/api/reports', $malformed_report_payload);\n        $request->assertStatus(422);\n        $this->assertDatabaseCount('reports', 0);\n    }",
			"start_line": 116,
			"end_line": 125,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_create_report_default_status_and_priority",
			"code": "public function test_create_report_default_status_and_priority(): void {\n\n        $report_payload = Report::factory()->make([\n            'priority'=>-1,\n            'status'=>0,\n        ])->toArray();\n\n        $request = $this->json('post', '/api/reports', $report_payload);\n        $request->assertStatus(200);\n        $this->assertDatabaseHas('reports', $report_payload);\n        $this->assertDatabaseCount('reports', 1);\n    }",
			"start_line": 131,
			"end_line": 142,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_create_report_base",
			"code": "public function test_create_report_base(): void {\n\n        $report_payload = Report::factory()->make()->toArray();\n\n        $request = $this->json('post', '/api/reports', $report_payload);\n        $request->assertStatus(200);\n\n        $report_payload['priority'] = -1;\n        $report_payload['status'] = 0;\n\n        $this->assertDatabaseHas('reports', $report_payload);\n        $this->assertDatabaseCount('reports', 1);\n    }",
			"start_line": 148,
			"end_line": 160,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_create_report_with_responses",
			"code": "public function test_create_report_with_responses(): void {\n\n        $question = Question::create([\n            'question_description'=>\"This is a question\",\n            'is_open'=>false,\n            'is_active'=>false,\n        ]);\n        $answer = Answer::create([\n            'answer'=>\"this is an answer\",\n            'question_id'=>$question->id\n        ]);\n\n        $report_payload = [\n            'description'=>\"This is a test report\",\n            'submitter_email'=>\"test@testing.nl\",\n            'notify_submitter'=>false,\n            'responses' => [\n                '1'=>[\n                    \"question_id\"=> $question->id,\n                    \"answer_id\"=> $answer->id\n                ],\n            ]\n        ];\n\n\n\n        $request = $this->json('post', '/api/reports', $report_payload);\n        // $this->assertEquals(1,2, json_decode($request->getContent()));\n        $request->assertStatus(200);\n        $this->assertDatabaseCount('reports', 1);\n        $this->assertDatabaseCount('responses', 1);\n\n        $response_body = [\n            \"question_id\"=> $question->id,\n            \"answer_id\"=> $answer->id,\n            \"report_id\"=>json_decode($request->getContent())[1]->id\n        ];\n        $this->assertDatabaseHas('responses', $response_body);\n    }",
			"start_line": 167,
			"end_line": 205,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_get_report_with_responses",
			"code": "public function test_get_report_with_responses(): void {\n        Sanctum::actingAs(User::factory()->create());\n\n        $report = Report::factory()->create();\n        // = [\n        //     'description'=>\"This is a test report\",\n        //     'priority'=>1,\n        //     'status'=>0,\n        //     'submitter_email'=>\"test@testing.nl\"\n        // ];\n        // $report = Report::create($report_body);\n\n        // Questions and answer model entities.\n        $question = Question::create([\n            'question_description'=>\"This is a question\",\n            'is_open'=>false,\n            'is_active'=>false,\n        ]);\n        $answer = Answer::create([\n            'answer'=>\"this is an answer\",\n            'question_id'=>$question->id\n        ]);\n\n        // response body and model entity\n        $response_body = [\n            \"question_id\"=> $question->id,\n            \"answer_id\"=> $answer->id,\n            \"report_id\"=> $report->id\n        ];\n        $response = new Response();\n        $response->question_id = $question->id;\n        $response->answer_id = $answer->id;\n        $response->report_id = $report->id;\n        $report->response()->save($response);\n\n\n        // Test database entry counts of the following tables\n        $this->assertDatabaseCount('reports', 1);\n        $this->assertDatabaseCount('questions', 1);\n        $this->assertDatabaseCount('answers', 1);\n        $this->assertDatabaseCount('responses', 1);\n\n        $response = $this->get('api/reports/'.$report->id);\n        $response->assertStatus(200);\n        $response->assertSee($report->toArray);\n        $response->assertSee($response_body);\n    }",
			"start_line": 211,
			"end_line": 257,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_patch_report_invalid_request",
			"code": "public function test_patch_report_invalid_request(): void {\n        Sanctum::actingAs(User::factory()->create());\n\n        $payload = [\n            'status' => 8,\n            'priority' => 8\n        ];\n\n        $response = $this->json('PATCH', \"/api/reports/1\", $payload);\n        $response->assertStatus(400);\n    }",
			"start_line": 263,
			"end_line": 273,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_patch_report_valid_request",
			"code": "public function test_patch_report_valid_request(): void {\n        $user = User::factory()->create();\n        Sanctum::actingAs($user);\n        $status = 777;\n        $priority = 888;\n        $payload = [\n            'status' => $status,\n            'priority' => $priority,\n            'user_id' => $user->id,\n        ];\n\n        $report_body = [\n            'description'=>\"This is a test report\",\n            'priority'=>1,\n            'status'=>0,\n            'submitter_email'=>\"test@testing.nl\",\n            'notify_submitter' => true,\n        ];\n        $report = Report::create($report_body);\n        $this->assertDatabaseCount('reports', 1);\n\n        $response = $this->json('PATCH', \"/api/reports/\".$report->id, $payload);\n        $response->assertStatus(200);\n        $response->assertSee($report->description);\n        $response->assertSee($report->submitter_email);\n        $response->assertSee($report->user_id);\n        $response->assertSee($priority);\n        $response->assertSee($status);\n    }",
			"start_line": 279,
			"end_line": 307,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_get_reports_with_status_filter",
			"code": "public function test_get_reports_with_status_filter(): void {\n        Sanctum::actingAs(User::factory()->create());\n\n        $report_body1= [\n            'description'=>\"This is a unique description with status = 0\",\n            'priority'=>0,\n            'status'=>0,\n            'submitter_email'=>\"test@testing.nl\",\n        ];\n        $report_body2 = [\n            'description'=>\"This is a test report with status = 1\",\n            'priority'=>6,\n            'status'=>1,\n            'submitter_email'=>\"test@testing.nl\",\n        ];\n        $report_body3 = [\n            'description'=>\"This is a very random message\",\n            'priority'=>10,\n            'status'=>2,\n            'submitter_email'=>\"test@testing.nl\",\n        ];\n        $report1 = Report::create($report_body1);\n        $report2 = Report::create($report_body2);\n        $report3 = Report::create($report_body3);\n        $this->assertDatabaseCount('reports', 3);\n\n        $payload = [\n            \"status\" => \"0\"\n        ];\n\n\n        $response = $this->json('get', '/api/reports', $payload);\n        $response->assertStatus(200);\n        // finding unique report with description\n        $response->assertSee($report1->description);\n        $response->assertDontSee($report2->description);\n        $response->assertDontSee($report3->description);\n    }",
			"start_line": 313,
			"end_line": 350,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_get_reports_with_priority_filter",
			"code": "public function test_get_reports_with_priority_filter(): void {\n        Sanctum::actingAs(User::factory()->create());\n\n        $report_body1= [\n            'description'=>\"This is a unique description with status = 0\",\n            'priority'=>0,\n            'status'=>0,\n            'submitter_email'=>\"test@testing.nl\",\n        ];\n        $report_body2 = [\n            'description'=>\"This is a test report with status = 1\",\n            'priority'=>6,\n            'status'=>1,\n            'submitter_email'=>\"test@testing.nl\",\n        ];\n        $report_body3 = [\n            'description'=>\"This is a very random message\",\n            'priority'=>10,\n            'status'=>2,\n            'submitter_email'=>\"test@testing.nl\",\n        ];\n        $report1 = Report::create($report_body1);\n        $report2 = Report::create($report_body2);\n        $report3 = Report::create($report_body3);\n        $this->assertDatabaseCount('reports', 3);\n\n        $payload = [\n            \"priority\" => \"0\"\n        ];\n\n        $response = $this->json('get', '/api/reports', $payload);\n        $response->assertStatus(200);\n        // finding unique report with description\n        $response->assertSee($report1->description);\n        $response->assertDontSee($report2->description);\n        $response->assertDontSee($report3->description);\n    }",
			"start_line": 356,
			"end_line": 392,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_get_reports_with_insufficient_authorization",
			"code": "public function test_get_reports_with_insufficient_authorization(): void {\n        $response = $this->json('GET', \"/api/reports\");\n        $response->assertUnauthorized();\n    }",
			"start_line": 398,
			"end_line": 401,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_get_report_with_insufficient_authorization",
			"code": "public function test_get_report_with_insufficient_authorization(): void {\n        $response = $this->json('GET', \"/api/reports/1\");\n        $response->assertUnauthorized();\n    }",
			"start_line": 407,
			"end_line": 410,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_patch_report_with_insufficient_authorization",
			"code": "public function test_patch_report_with_insufficient_authorization(): void {\n        $response = $this->json('PATCH', \"/api/reports/1\");\n        $response->assertUnauthorized();\n    }",
			"start_line": 416,
			"end_line": 419,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		},
		{
			"type": "method_declaration",
			"name": "test_patch_report_invalid_user_id_request",
			"code": "public function test_patch_report_invalid_user_id_request(): void {\n        $user = User::factory()->create();\n        Sanctum::actingAs($user);\n        $payload = [\n            'status' => 1,\n            'priority' => 1,\n            'user_id' => $user->id+1,\n        ];\n        $report = Report::factory()->create();\n        $this->assertDatabaseCount('reports', 1);\n\n        $response = $this->json('PATCH', \"/api/reports/\".$report->id, $payload);\n        $response->assertStatus(400);\n        $response->assertSee(\"ERROR: passed non-existing user id\");\n    }",
			"start_line": 425,
			"end_line": 439,
			"file": "/tmp/tmp28s_d8z_/ReportsTest.php",
			"language": "php"
		}
	]
}

print(return_similarity_matches(req_json_test, func_json_test, 3, False))
"""
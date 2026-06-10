from brain.llm_manager import LLMManager
from brain.entity_extractor import EntityExtractor

from memory.short_term import ShortTermMemory
from memory.context_manager import ContextManager
from memory.preference import PreferenceMemory
from memory.long_term import LongTermMemory

from brain.response_generator import ResponseGenerator

from planner.planner import Planner

from tools.tool_router import ToolRouter
from tools.executor import ToolExecutor


class ConversationManager:

    def __init__(self):

        # Core AI systems
        self.llm = LLMManager()

        self.extractor = EntityExtractor()

        # Memory systems
        self.memory = ShortTermMemory()

        self.long_term = LongTermMemory()

        self.context_manager = ContextManager()

        self.preferences = PreferenceMemory()

        # Load saved preferences from long-term memory
        stored_preferences = self.long_term.load()

        for key, value in stored_preferences.items():

            self.preferences.save(
                key,
                value
            )

        # Response system
        self.response_generator = ResponseGenerator()

        # Planning system
        self.planner = Planner()

        # Tool systems
        self.router = ToolRouter()

        self.executor = ToolExecutor()

    def process_message(self, message):

        # =========================================
        # Step 1: Understand message
        # =========================================
        analysis = self.llm.understand(
            message
        )

        # =========================================
        # Step 2: Extract entities
        # =========================================
        entities = self.extractor.extract(
            message
        )

        # =========================================
        # Step 3: Build new context
        # =========================================
        new_context = {

            "intent": analysis["intent"],

            "entities": entities
        }

        # =========================================
        # Step 4: Load old context
        # =========================================
        old_context = self.memory.get(
            "current_context"
        )

        # =========================================
        # Step 5: Merge contexts
        # =========================================
        merged_context = self.context_manager.merge(
            old_context,
            new_context
        )

        # =========================================
        # Step 6: Save short-term memory
        # =========================================
        self.memory.save(
            "current_context",
            merged_context
        )

        # =========================================
        # Step 7: Learn preferences
        # =========================================
        if "time" in merged_context["entities"]:

            meeting_time = merged_context[
                "entities"
            ]["time"]

            self.preferences.add_history(
                "meeting_time",
                meeting_time
            )

            history = self.preferences.get_history(
                "meeting_time"
            )

            # Learn after repeated behavior
            if len(history) >= 3:

                self.preferences.save(
                    "preferred_meeting_time",
                    "Afternoon"
                )

        # =========================================
        # Step 8: Save long-term memory
        # =========================================
        self.long_term.save(
            self.preferences.get_all()
        )

        # =========================================
        # Step 9: Generate natural response
        # =========================================
        response = self.response_generator.generate(
            merged_context,
            self.preferences.get_all()
        )

        # =========================================
        # Step 10: Create plan
        # =========================================
        plan = self.planner.create_plan(
            merged_context
        )

        # =========================================
        # Step 11: Route tools
        # =========================================
        tools = self.router.route(
            plan
        )

        # =========================================
        # Step 12: Execute tools
        # =========================================
        execution_results = self.executor.execute(
            plan,
            merged_context
        )

        # =========================================
        # Step 13: Final response
        # =========================================
        return {

            "response": response,

            "plan": plan,

            "tools": tools,

            "execution": execution_results,

            "memory": self.memory.get_all(),

            "preferences": self.preferences.get_all(),

            "long_term": self.long_term.load()
        }
from typing import overload

from groq.types.chat import (
	ChatCompletionAssistantMessageParam,
	ChatCompletionContentPartImageParam,
	ChatCompletionContentPartTextParam,
	ChatCompletionMessageParam,
	ChatCompletionMessageToolCallParam,
	ChatCompletionSystemMessageParam,
	ChatCompletionUserMessageParam,
)
from groq.types.chat.chat_completion_content_part_image_param import ImageURL
from groq.types.chat.chat_completion_message_tool_call_param import Function

from browser_use.llm.messages import (
	AssistantMessage,
	BaseMessage,
	ContentPartImageParam,
	ContentPartRefusalParam,
	ContentPartTextParam,
	SystemMessage,
	ToolCall,
	UserMessage,
)


class GroqMessageSerializer:
	"""Serializer for converting between custom message types and OpenAI message param types."""

	@staticmethod
	def _serialize_content_part_text(part: ContentPartTextParam) -> ChatCompletionContentPartTextParam:
		return ChatCompletionContentPartTextParam(text=part.text, type='text')

	@staticmethod
	def _serialize_content_part_image(part: ContentPartImageParam) -> ChatCompletionContentPartImageParam:
		return ChatCompletionContentPartImageParam(
			image_url=ImageURL(url=part.image_url.url, detail=part.image_url.detail),
			type='image_url',
		)

	@staticmethod
	def _serialize_user_content(
		content: str | list[ContentPartTextParam | ContentPartImageParam],
	) -> str | list[ChatCompletionContentPartTextParam | ChatCompletionContentPartImageParam]:
		"""Serialize content for user messages (text and images allowed)."""
		if isinstance(content, str):
			return content

		serialized_parts: list[ChatCompletionContentPartTextParam | ChatCompletionContentPartImageParam] = []
		for part in content:
			if part.type == 'text':
				serialized_parts.append(GroqMessageSerializer._serialize_content_part_text(part))
			elif part.type == 'image_url':
				serialized_parts.append(GroqMessageSerializer._serialize_content_part_image(part))
		return serialized_parts

	@staticmethod
	def _serialize_system_content(
		content: str | list[ContentPartTextParam],
	) -> str:
		"""Serialize content for system messages (text only)."""
		if isinstance(content, str):
			return content

		serialized_parts: list[str] = []
		for part in content:
			if part.type == 'text':
				serialized_parts.append(GroqMessageSerializer._serialize_content_part_text(part)['text'])

		return '\n'.join(serialized_parts)

	@staticmethod
	def _serialize_assistant_content(
		content: str | list[ContentPartTextParam | ContentPartRefusalParam] | None,
	) -> str | None:
		"""Serialize content for assistant messages (text and refusal allowed)."""
		if content is None:
			return None
		if isinstance(content, str):
			return content

		serialized_parts: list[str] = []
		for part in content:
			if part.type == 'text':
				serialized_parts.append(GroqMessageSerializer._serialize_content_part_text(part)['text'])

		return '\n'.join(serialized_parts)

	@staticmethod
	def _serialize_tool_call(tool_call: ToolCall) -> ChatCompletionMessageToolCallParam:
		return ChatCompletionMessageToolCallParam(
			id=tool_call.id,
			function=Function(name=tool_call.function.name, arguments=tool_call.function.arguments),
			type='function',
		)

	# endregion

	# region - Serialize overloads
	@overload
	@staticmethod
	def serialize(message: UserMessage) -> ChatCompletionUserMessageParam: ...

	@overload
	@staticmethod
	def serialize(message: SystemMessage) -> ChatCompletionSystemMessageParam: ...

	@overload
	@staticmethod
	def serialize(message: AssistantMessage) -> ChatCompletionAssistantMessageParam: ...

	@staticmethod
	def serialize(message: BaseMessage) -> ChatCompletionMessageParam:
		"""Serialize a custom message to an OpenAI message param."""

		if isinstance(message, UserMessage):
			user_result: ChatCompletionUserMessageParam = {
				'role': 'user',
				'content': GroqMessageSerializer._serialize_user_content(message.content),
			}
			if message.name is not None:
				user_result['name'] = message.name
			return user_result

		elif isinstance(message, SystemMessage):
			system_result: ChatCompletionSystemMessageParam = {
				'role': 'system',
				'content': GroqMessageSerializer._serialize_system_content(message.content),
			}
			if message.name is not None:
				system_result['name'] = message.name
			return system_result

		elif isinstance(message, AssistantMessage):
			# Handle content serialization
			content = None
			if message.content is not None:
				content = GroqMessageSerializer._serialize_assistant_content(message.content)

			assistant_result: ChatCompletionAssistantMessageParam = {'role': 'assistant'}

			# Only add content if it's not None
			if content is not None:
				assistant_result['content'] = content

			if message.name is not None:
				assistant_result['name'] = message.name

			if message.tool_calls:
				assistant_result['tool_calls'] = [GroqMessageSerializer._serialize_tool_call(tc) for tc in message.tool_calls]

			return assistant_result

		else:
			raise ValueError(f'Unknown message type: {type(message)}')

	@staticmethod
	def serialize_messages(messages: list[BaseMessage]) -> list[ChatCompletionMessageParam]:
		return [GroqMessageSerializer.serialize(m) for m in messages]

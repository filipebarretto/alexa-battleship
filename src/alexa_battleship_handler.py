# -*- coding: utf-8 -*-

import json
import logging
import boto3
import random

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.dispatch_components import (
AbstractRequestHandler, AbstractExceptionHandler,
AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.response_helper import (
get_plain_text_content, get_rich_text_content)

from ask_sdk_model.interfaces.display import (
ImageInstance, Image, RenderTemplateDirective, ListTemplate1,
BackButtonBehavior, ListItem, BodyTemplate2, BodyTemplate1)
from ask_sdk_model import ui, Response

from custom_modules import data, util, dbcontroller, drawboard
    

# Skill Builder object
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#iot = boto3.client('iot-data', region_name='us-east-1')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

STATE_LAUNCH = "launch_state"
STATE_NEW_GAME = "new_game"
STATE_SETTING_UP_BOARD = "setting_up_board"
STATE_PLAY_GAME = "play_game"


# Request Handler classes
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        
        user_id = handler_input.request_envelope.session.user.user_id
        response_builder = handler_input.response_builder
        
        empty_board = util.clear_board()
        
        rsp = data.WELCOME_MESSAGE
        
        r = drawboard.draw_board_with_ships(user_id, empty_board, "user")
        print(r)
        
        user_board_image = dbcontroller.get_board_img(user_id, "user")
        response_builder.set_card(ui.StandardCard(
                                                  title = "Battleship",
                                                  text = rsp,
                                                  image = ui.Image(small_image_url = user_board_image, large_image_url = user_board_image)))
            
        response_builder.speak(rsp).ask(rsp)
        return response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for skill session end."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")
        print("Session ended with reason: {}".format(handler_input.request_envelope))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")
        handler_input.attributes_manager.session_attributes = {}
        # Resetting session
        
        handler_input.response_builder.speak(data.HELP_MESSAGE).ask(data.HELP_MESSAGE)
        return handler_input.response_builder.response


class ExitIntentHandler(AbstractRequestHandler):
    """Single Handler for Cancel, Stop and Pause intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExitIntentHandler")
        handler_input.response_builder.speak(
                                             data.EXIT_SKILL_MESSAGE).set_should_end_session(True)
        return handler_input.response_builder.response



class ListShipsHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return (is_intent_name("list_ships")(handler_input))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ListShipsHandler")
        attr = handler_input.attributes_manager.session_attributes
        
        rsp = random.choice(data.LIST_SHIPS_RESPONSE)
        
        #for ship in data.SHIPS:
        for i in range(len(data.SHIPS)):
            ship = data.SHIPS[i]
            rsp += ship + ", " if i < (len(data.SHIPS) - 1) else data.AND + " " + ship + "."
        
        response_builder = handler_input.response_builder
        response_builder.speak(rsp)
        
        return response_builder.response



class SetupBoardHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return (is_intent_name("setup_board")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SetupBoardHandler")
        attr = handler_input.attributes_manager.session_attributes

        attr["board"] = util.clear_board()
        attr["state"] = STATE_SETTING_UP_BOARD
        attr["setup_board_ship_code"] = data.PIECES["patrol_boat"]["code"]
        attr["setup_board_ship_count"] = 0
        
        user_id = handler_input.request_envelope.session.user.user_id
        response_builder = handler_input.response_builder
        
        rsp = random.choice(data.PLACE_PIECE_RESPONSE) + data.SHIPS[0] + ", " + random.choice(data.PLACE_PIECE_SIZE) + str(data.PIECES[util.get_ship_id(data.SHIPS[0])]["size"]) + "?"

        r = drawboard.draw_board_with_ships(user_id, attr["board"], "user")
        print(r)
        
        user_board_image = dbcontroller.get_board_img(user_id, "user")
        response_builder.set_card(ui.StandardCard(
                                                  title = data.SHIPS[0].title(),
                                                  text = rsp,
                                                  image = ui.Image(small_image_url = user_board_image, large_image_url = user_board_image)))
    
        response_builder.speak(rsp).ask(rsp)

        return response_builder.response


# PLACES PIECE IN BOARD TO SETUP GAME
class PlacePieceHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        state = attr.get("state")
        setup_ship_count = attr.get("setup_board_ship_count", 0)
        return (is_intent_name("place_piece")(handler_input) and state == STATE_SETTING_UP_BOARD and setup_ship_count < len(data.PIECES.keys()))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlacePieceHandler")
        attr = handler_input.attributes_manager.session_attributes

        setup_ship_code = attr.get("setup_board_ship_code")
        setup_ship_count = attr.get("setup_board_ship_count", 0)
        
        print("Placing ship with code: " + str(setup_ship_code))
        
        slots = handler_input.request_envelope.request.intent.slots
        print(slots)
        
        start_square = slots["start_square"].resolutions.resolutions_per_authority[0].values[0].value.id
        print("start_square = " + start_square)
        start = util.get_square(start_square)
        print("start = " + str(start))
        
        end_square = slots["end_square"].resolutions.resolutions_per_authority[0].values[0].value.id
        print("end_square = " + end_square)
        end = util.get_square(end_square)
        print("end = " + str(end))
        
        placement = util.place_piece(attr["board"], util.get_ship_id(data.SHIPS[setup_ship_count]), start, end)
        
        print("Current board: ")
        print(placement["board"])
        
        response_builder = handler_input.response_builder
        user_id = handler_input.request_envelope.session.user.user_id
        
        if placement["is_legal"]:
            attr["board"] = placement["board"]
            setup_ship_count += 1
            
            if setup_ship_count < len(data.PIECES.keys()):
                attr["setup_board_ship_code"] = data.PIECES[util.get_ship_id(data.SHIPS[setup_ship_count])]["code"]
                attr["setup_board_ship_count"] = setup_ship_count
                
                rsp = random.choice(data.PLACE_PIECE_RESPONSE) + data.SHIPS[setup_ship_count] + ", " + random.choice(data.PLACE_PIECE_SIZE) + str(data.PIECES[util.get_ship_id(data.SHIPS[setup_ship_count])]["size"]) + "?"
                
                r = drawboard.draw_board_with_ships(user_id, placement["board"], "user")
                print(r)
                
                user_board_image = dbcontroller.get_board_img(user_id, "user")
                response_builder.set_card(ui.StandardCard(
                                                          title = data.SHIPS[setup_ship_count].title(),
                                                          text = rsp,
                                                          image = ui.Image(small_image_url = user_board_image, large_image_url = user_board_image)))
                                                          
                response_builder.speak(rsp).ask(rsp)
                return response_builder.response
            else:
                attr["state"] = STATE_PLAY_GAME
                attr["setup_board_ship_code"] = None
                attr["setup_board_ship_count"] = 0
                
                response = dbcontroller.save_board(user_id, placement["board"], util.get_random_board(), 0, 0)
                print(response)
                
                r = drawboard.draw_board_with_ships(user_id, placement["board"], "user")
                print(r)
                
                board_image = dbcontroller.get_board_img(user_id, "user")
                response_builder.set_card(ui.StandardCard(
                                                          title = "Battleship",
                                                          text = "Board ready to start the game.",
                                                          image = ui.Image(small_image_url = board_image, large_image_url = board_image)))
                
                rsp = random.choice(data.BOARD_READY) + random.choice(data.ATTACK)
                response_builder.speak(rsp).ask(rsp)
                return response_builder.response
                
        else:
            rsp = random.choice(data.ILLEGAL_PLACEMENT) + placement.get("msg", data.UNEXPECTED_ERROR) + random.choice(data.PLACE_PIECE_RESPONSE) + data.SHIPS[setup_ship_count] + "?"

            r = drawboard.draw_board_with_ships(user_id, placement["board"], "user")
            print(r)

            user_board_image = dbcontroller.get_board_img(user_id, "user")
            response_builder.set_card(ui.StandardCard(
                                                      title = data.SHIPS[setup_ship_count].title(),
                                                      text = rsp,
                                                      image = ui.Image(small_image_url = user_board_image, large_image_url = user_board_image)))

            response_builder.speak(rsp).ask(rsp)
            return response_builder.response

# TODO RESUME GAME

class PlayerTurnHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        state = attr.get("state")
        return (is_intent_name("player_turn")(handler_input) and state == STATE_PLAY_GAME)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlayerTurnHandler")
        attr = handler_input.attributes_manager.session_attributes
        response_builder = handler_input.response_builder
        
        slots = handler_input.request_envelope.request.intent.slots
        print(slots)
        user_target_slot = slots["target_square"].resolutions.resolutions_per_authority[0].values[0].value.id
        print("user_target_slot_id: " + str(user_target_slot))

        user_target_square = util.get_square(user_target_slot)
        print("user_target_square: " + str(user_target_square))
        
        # TODO GET BOARD FROM DYNAMODB
        # board = attr.get("board")
        user_id = handler_input.request_envelope.session.user.user_id
        current_game = dbcontroller.load_board(user_id)
        print(current_game)
        user_board = current_game.get("user_board")
        print("user_board: ")
        print(user_board)
        print("opponent_board: ")
        opponent_board = current_game.get("opponent_board")
        print(opponent_board)
        
        
        user_hits = current_game.get("user_hits")
        opponent_hits = current_game.get("opponent_hits")
        

        user_attack = util.attack_square(user_target_square, opponent_board)
        user_id = handler_input.request_envelope.session.user.user_id
        
        # TODO: CHECK IF PLAYERS HAVE WON
        if user_attack.get("is_legal"):
            
            user_hits += 1 if user_attack.get("hit") else 0
            
            # OPPONENTS ATTACK
            opponent_attack = util.opponent_attack_square(user_board)
            opponent_hits += 1 if user_attack.get("hit") else 0
            
            response = dbcontroller.save_board(user_id, opponent_attack.get("board"), user_attack.get("board"), user_hits, opponent_hits)
            print(response)

            r = drawboard.draw_board_without_ships(user_id, user_attack.get("board"), "opponent")
            print(r)
            
            rsp = data.YOU + user_attack.get("msg") + data.OPPONENT + opponent_attack.get("msg") + random.choice(data.ATTACK)
            
            opponent_board_image = dbcontroller.get_board_img(user_id, "opponent")
            response_builder.set_card(ui.StandardCard(
                                                      title = "Battleship",
                                                      text = rsp,
                                                      image = ui.Image(small_image_url = opponent_board_image, large_image_url = opponent_board_image)))
            
            
            response_builder.speak(rsp).ask(rsp)
            return response_builder.response
        else:
            
            r = drawboard.draw_board_without_ships(user_id, user_attack.get("board"), "opponent")
            print(r)
            
            rsp = user_attack.get("msg") + random.choice(data.ATTACK)
            
            opponent_board_image = dbcontroller.get_board_img(user_id, "opponent")
            response_builder.set_card(ui.StandardCard(
                                                      title = "Battleship",
                                                      text = rsp,
                                                      image = ui.Image(small_image_url = opponent_board_image, large_image_url = opponent_board_image)))
                                                      
            response_builder.speak(rsp).ask(rsp)
            return response_builder.response
        

class RepeatHandler(AbstractRequestHandler):
    """Handler for repeating the response to the user."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In RepeatHandler")
        attr = handler_input.attributes_manager.session_attributes
        response_builder = handler_input.response_builder
        if "recent_response" in attr:
            cached_response_str = json.dumps(attr["recent_response"])
            cached_response = DefaultSerializer().deserialize(
                                                              cached_response_str, Response)
            return cached_response
        else:
            response_builder.speak(data.FALLBACK_ANSWER).ask(data.HELP_MESSAGE)
            
            return response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for handling fallback intent.
        2018-May-01: AMAZON.FallackIntent is only currently available in
        en-US locale. This handler will not be triggered except in that
        locale, so it can be safely deployed for any locale."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        handler_input.response_builder.speak(data.FALLBACK_ANSWER).ask(data.HELP_MESSAGE)
                                             
        return handler_input.response_builder.response


# Interceptor classes
class CacheResponseForRepeatInterceptor(AbstractResponseInterceptor):
    """Cache the response sent to the user in session.
        The interceptor is used to cache the handler response that is
        being sent to the user. This can be used to repeat the response
        back to the user, in case a RepeatIntent is being used and the
        skill developer wants to repeat the same information back to
        the user.
        """
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["recent_response"] = response


# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.
        This handler catches all kinds of exceptions and prints
        the stack trace on AWS Cloudwatch with the request envelope."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True
    
    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        
        handler_input.response_builder.speak(data.ERROR_MESSAGE).ask(data.ERROR_MESSAGE)
        
        attr = handler_input.attributes_manager.session_attributes
        attr["state"] = ""
        
        return handler_input.response_builder.response

# Request and Response Loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
                                                  handler_input.request_envelope))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))



# Add all request handlers to the skill.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(RepeatHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())


# Add all request handlers to the skill.
sb.add_request_handler(ListShipsHandler())
sb.add_request_handler(SetupBoardHandler())
sb.add_request_handler(PlacePieceHandler())
sb.add_request_handler(PlayerTurnHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
sb.add_global_response_interceptor(CacheResponseForRepeatInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()


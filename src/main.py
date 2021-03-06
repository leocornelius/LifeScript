from lexer import Lexer
from parser_class import Parser
import traceback
import logging
import coloredlogs
from argparse import ArgumentParser
from prelude import prelude
import memory
import pickle
DEBUG = True

lexer = Lexer().get_lexer()
pg = Parser()
pg.parse()
parser = pg.get_parser()
logger = logging.getLogger(__name__)
prelude()
coloredlogs.install(level=logging.DEBUG)
argparser = ArgumentParser()
argparser.add_argument("-f", "--file", dest="filename",
                       help="file to run", metavar="FILE")
argparser.add_argument("-i", "--ide", dest="ide",
                       help="Run in IDE mode")

args = argparser.parse_args()


def print_nested_children(node):
    print(node)
    if hasattr(node, "iter"):
        for child in node.iter():
            print_nested_children(child)


def export_ast(ast):
    with open("ast.pickle", "wb") as file:
        import json
        pickle.dump(ast, file)


def import_ast():
    global DEBUG
    with open("ast.pickle", "rb") as file:
        ast = pickle.load(file)
        if DEBUG:
            print_nested_children(ast)
        return ast


def main(args):
    global DEBUG
    program = None
    if args.filename:
        program = args.filename
    elif args.ide:
        program = "ide.ls"
    else:
        program = input("Enter program: ")
    if program == "ide.ls":
        while True:
            try:
                text_input = input(">> ")
                if text_input == "exit()":
                    break
                elif text_input == "clear()":
                    print("\n" * 100)
                    # clear the global_context
                    memory.clear()
                    prelude()
                    continue
                elif text_input == "debug()":
                    DEBUG = not DEBUG
                    logger.info("Debug mode is %s", DEBUG)
                    continue
                elif text_input == "help()":
                    print("Here are a list of commands for the IDE: ")
                    print("exit: Exits the IDE")
                    print(
                        "clear(): Restarts the session (clears screen as well as the VM varible list")
                    print("help(): Prints this list")
                    print("debug(): Toggles debug mode")
                    print("load(): Load the ast pickle file")
                    continue
                elif text_input == "load()":
                    ast = import_ast()
                    ast.eval()
                    continue
                elif text_input == "":
                    continue
                tokens = lexer.lex(text_input)
                if DEBUG:
                    for token in tokens:
                        logging.debug((token))
                    tokens = lexer.lex(text_input)  # relex

                ast_tree = parser.parse(tokens)
                if DEBUG:
                    # iterate over the children of the children of the ast tree
                    export_ast(ast_tree)
                    print_nested_children(ast_tree)
                    print("----")
                    print("\n")

                if ast_tree is not None:
                    ast_tree.eval()
            except Exception as e:
                if (e == KeyboardInterrupt):
                    print("\n")
                    break
                if DEBUG:
                    traceback.print_exc()
                else:
                    logging.error(e)
                logging.critical("VM crashed, resuming execution runtime")
    else:
        with open(program, "r") as file:
            text_input = file.read()
            # tokenize the input
            tokens = lexer.lex(text_input)
            if DEBUG:
                for token in tokens:
                    logging.debug((token))
                tokens = lexer.lex(text_input)  # relex

            ast_tree = parser.parse(tokens)
            if DEBUG:
                # iterate over the children of the children of the ast tree
                print(ast_tree)
                print("----")
                print("\n")

            print("-------------------------------------")
            print("\n")
            if ast_tree is not None:
                ast_tree.eval()
            else:
                print("No AST tree generated")


main(args)

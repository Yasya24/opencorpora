#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import codecs
import os
import argparse
import xml.sax
import datetime

import opcorp_parsers
import no_homonymy_constants



STRATEGY_ALL = 'a'
STRATEGY_MAJORITY = 'm'

POOL_FILENAME = 'pools.txt'
POOL_FILE_PREFIX = 'pool_'
POOL_FILE_EXT = '.tab'
POOL_FILE_DELIMITER = '\t'

POOL_FILE_DECISION_TOKEN_INDEX = 1
POOL_FILE_DECISION_DECISION_INDEX = 4

POOL_DECSRIPTION_POOL_INDEX = 0
POOL_DECSRIPTION_STATUS_INDEX = -1
POOL_DECSRIPTION_TYPE_INDEX = 1

POOL_MODERATED_STATUS = 9



def generate_no_homonymy_dump(poolFolder, homonymyCorpusFilename, strategy, is_to_print_time):
    start = datetime.datetime.now()
    
    tokensWithAgreement = findTokensWithAgreement(poolFolder, strategy)
    
    if is_to_print_time:
        print('time elapsed for tokensWithAgreement:{0}'.format(datetime.datetime.now() - start))
        
    if not tokensWithAgreement:
        print('no tokens in unmoderated pools which annotators agreed on')
        return  
    remove_homonymy_for_tokens(homonymyCorpusFilename, tokensWithAgreement, is_to_print_time)
    
    
    
    
def remove_homonymy_for_tokens(homonymyCorpusFilename, tokensWithAgreement, is_to_print_time):
    start = datetime.datetime.now()
    removedVariantsFilename, tokens_max_variant_arrays = copy_xml_removing_variants(homonymyCorpusFilename, tokensWithAgreement)
    
    if is_to_print_time:
        print('time elapsed for remove_homonymy_for_tokens:{0}'.format(datetime.datetime.now() - start))
    
    
    start = datetime.datetime.now()
    normalizedFilename = homonymyCorpusFilename + '_removed.xml'
    normalize_corpus_file(removedVariantsFilename, normalizedFilename, tokens_max_variant_arrays)
    
    if is_to_print_time:
        print('time elapsed for normalize_corpus_file:{0}'.format(datetime.datetime.now() - start))
    
def copy_xml_removing_variants(homonymyCorpusFilename, tokensWithAgreement):
    removedVariantsFilename = homonymyCorpusFilename + '_removed_temp.xml'
    
    handler = opcorp_parsers.OpcorpTokenVariantRemover(removedVariantsFilename, tokensWithAgreement, 'utf-8')
    xml.sax.parse(homonymyCorpusFilename, handler)
    return removedVariantsFilename, handler.tokens_max_variant_arrays
    
def normalize_corpus_file(removedVariantsFilename, normalizedFilename, tokens_max_variant_arrays):
    handler = opcorp_parsers.OpcorpTokenNormalizer(normalizedFilename, tokens_max_variant_arrays, 'utf-8')
    xml.sax.parse(removedVariantsFilename, handler)


def findTokensWithAgreement(poolFolder, strategy):
    return getTokensWithAgreementFromPools(getUnmoderatedPools(poolFolder), poolFolder, strategy)

def getTokensWithAgreementFromPools(unmoderatedPools, poolFolder, strategy):
    tokens = {}
    for unmoderatedPool in unmoderatedPools:
        gatherTokensFromPool(unmoderatedPool, poolFolder, tokens, strategy)
    filterTokensWithAgreement(tokens, strategy) 
    return tokens

def gatherTokensFromPool(unmoderatedPool, poolFolder, tokens,strategy):
    poolFilename = os.path.join(poolFolder, POOL_FILE_PREFIX + unmoderatedPool[0] + POOL_FILE_EXT)
    if not os.path.exists(poolFilename):
        raise Exception('No pool file found %s ' % poolFilename)

    with codecs.open(poolFilename, 'r', 'utf-8') as fin:
        for line in fin:
            tokenDescriptionParts = line.strip().split(POOL_FILE_DELIMITER)
            tokenId = getTokenId(tokenDescriptionParts)
            
            
            
            tokenDecisions, moderatorsComment = getTokenDecisions(tokenDescriptionParts)
            
            #TODO: remove
            """if tokenId in [u"403727", u"473357", u"847270", u"848625", 
                           u"847340", u"846865", u"849749", u"684039", 
                           u"753426", u"604393", u"390802", u"23892", u"23897", 
                           u"322743", u"315855", u"539789", u"540572", u"214773", 
                           u"109581", u"109547", u"170191", u"499013", u"543749", 
                           u"161537", u"541098", u"296850", u"242804", u"437096", 
                           u"847324", u"23120", u"479986", u"473305", u"701841"]:
                print(tokenId + ' in ' + poolFilename + ' with ' + ','.join(tokenDecisions))"""
            
            if not isSuitableAccordingToStrategy(tokenDecisions, moderatorsComment, strategy):
                continue
            
            if tokenId in tokens:
                if unmoderatedPool[1] not in tokens[tokenId]:
                    tokens[tokenId][unmoderatedPool[1]] = []
                tokens[tokenId][unmoderatedPool[1]]['tokenDecisions'] += tokenDecisions
                tokens[tokenId][unmoderatedPool[1]]['moderatorsComment'] += moderatorsComment
                    
            else:
                tokens[tokenId] = {}
                tokens[tokenId][unmoderatedPool[1]] = {}
                tokens[tokenId][unmoderatedPool[1]]['tokenDecisions'] = tokenDecisions
                tokens[tokenId][unmoderatedPool[1]]['moderatorsComment'] = []
                
def filterTokensWithAgreement(tokens, strategy):
    for tokenId, tokenPoolDecisions in tokens.items():
        hasAllPoolTypesDeleted = True
        for poolType, taskDecisions in tokenPoolDecisions.items():
            decisions = taskDecisions['tokenDecisions']
            moderatorsComment = taskDecisions['moderatorsComment']
            strategyDecision = isSuitableAccordingToStrategy(decisions, moderatorsComment, strategy)
            if strategyDecision:
                hasAllPoolTypesDeleted = False
                tokens[tokenId][poolType] = strategyDecision
            else:
                tokens[tokenId][poolType] = None
                
        if hasAllPoolTypesDeleted:
            tokens[tokenId] = None
                        


def isSuitableAccordingToStrategy(tokenDecisions, moderatorsComment, strategy):
    if strategy['strategy_type'] == STRATEGY_ALL:
        return checkAllDecisions(tokenDecisions, moderatorsComment, strategy)
    else:
        raise Exception('unrecognized strategy: %s ' % (strategy['strategy_type']))
     
def checkAllDecisions(tokenDecisions, moderatorsComment, strategy):   
    if moderatorsComment and len(set(moderatorsComment)) == 1:
        return moderatorsComment[0]
    if strategy.get('min_number') is not None and (not tokenDecisions 
                                                   or len(tokenDecisions) < strategy.get('min_number')):
        return False
    if len(set(tokenDecisions)) > 1:
        return False
    if tokenDecisions[0] == no_homonymy_constants.DECISION_OTHER:
        return no_homonymy_constants.DECISION_UNKNOWN
    return tokenDecisions[0]



                
def getUnmoderatedPools(poolFolder):
    poolDescriptionPath = os.path.join(poolFolder, POOL_FILENAME)
    if not os.path.exists(poolDescriptionPath):
        raise Exception('No pool description file found %s ' % poolDescriptionPath)
    
    pools = set()
    
    with codecs.open(poolDescriptionPath, 'r', 'utf-8') as fin:
        for line in fin:
            lineParts = line.strip().split(POOL_FILE_DELIMITER)
            poolStatus = getPoolStatus(lineParts)
            if isUnmoderatedPool(poolStatus):
                pools.add((getPoolId(lineParts), getPoolType(lineParts)))
                
    return pools

def isUnmoderatedPool(poolStatus):
    return int(poolStatus) < POOL_MODERATED_STATUS
    
def getTokenId(tokenDescriptionParts):
    return tokenDescriptionParts[POOL_FILE_DECISION_TOKEN_INDEX]


def getTokenDecisions(tokenDescriptionParts):
    decisions = tokenDescriptionParts[POOL_FILE_DECISION_DECISION_INDEX:]
    moderatorsComment = []
    if '' in decisions:
        moderatorCommentIndex = decisions.index('')
        moderatorsComment = decisions[moderatorCommentIndex+1:]
        decisions = decisions[:moderatorCommentIndex]
    return decisions, moderatorsComment

def getPoolId(poolDescriptionParts):
    return poolDescriptionParts[POOL_DECSRIPTION_POOL_INDEX]

def getPoolStatus(poolDescriptionParts):
    return poolDescriptionParts[POOL_DECSRIPTION_STATUS_INDEX]

def getPoolType(poolDescriptionParts):
    return poolDescriptionParts[POOL_DECSRIPTION_TYPE_INDEX]


def process_args():
    parser = argparse.ArgumentParser(description="Exclude variants of annotation from the dump based on the annotators'"
                                                    "common decisions")
    
    parser.add_argument('corpus_dump',
                            help='path to the opencorpora xml file')

    parser.add_argument('pool_folder',
                            help='path to the folder containing pool data')
   
    parser.add_argument('-s', '--strategy',
                            help='strategy to use: a=all answers',
                            choices=['a'], default='a')
    
    parser.add_argument('-m', '--min_number',
                            help='minimum number of replies to use for strategy',
                            type=int, default=1)
 
    parser.add_argument('-t', '--time', action='store_true', default=False,
                            help='print execution time in the end')
    return parser.parse_args()

    
def main():
    args = process_args()
    
    strategy = {'strategy_type':args.strategy, 'min_number':args.min_number}
    
    
    #corpusFilename = 'D:\\Opencorpora\\annot.opcorpora.xml.byfile\\2942.xml'
    #corpusFilename = 'D:\\Opencorpora\\annot.opcorpora.xml.byfile\\224.xml'
    
    #corpusFilename = 'D:\\Opencorpora\\annot.opcorpora.xml\\annot.opcorpora.xml'
    generate_no_homonymy_dump(args.pool_folder, args.corpus_dump, strategy, args.time)
    
    
if __name__ == "__main__":
    main()
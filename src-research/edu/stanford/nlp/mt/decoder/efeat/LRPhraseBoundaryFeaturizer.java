package edu.stanford.nlp.mt.decoder.efeat;

import java.util.*;

import edu.stanford.nlp.mt.base.FeatureValue;
import edu.stanford.nlp.mt.base.Featurizable;
import edu.stanford.nlp.mt.base.Sequence;
import edu.stanford.nlp.mt.base.IString;
import edu.stanford.nlp.mt.decoder.feat.RuleFeaturizer;

/**
 * 
 * @author danielcer
 * 
 */
public class LRPhraseBoundaryFeaturizer implements
    RuleFeaturizer<IString, String> {
  public static final String FEATURE_PREFIX = "LRPB";
  public static final String PREFIX_L = ":l";
  public static final String PREFIX_R = ":r";
  public static final String PREFIX_SRC = ":s";
  public static final String PREFIX_TRG = ":t";

  public static final int DEFAULT_SIZE = 2;
  public static final boolean DEFAULT_DO_SOURCE = true;
  public static final boolean DEFAULT_DO_TARGET = true;
  public final boolean doSource;
  public final boolean doTarget;
  public final int size;

  public LRPhraseBoundaryFeaturizer() {
    size = DEFAULT_SIZE;
    doSource = DEFAULT_DO_SOURCE;
    doTarget = DEFAULT_DO_TARGET;
  }

  public LRPhraseBoundaryFeaturizer(String... args) {
    size = Integer.parseInt(args[0]);
    if (args.length == 1) {
      doSource = DEFAULT_DO_SOURCE;
      doTarget = DEFAULT_DO_TARGET;
      return;
    }
    doSource = Boolean.parseBoolean(args[1]);
    doTarget = Boolean.parseBoolean(args[2]);
  }

  @Override
  public List<FeatureValue<String>> ruleFeaturize(
      Featurizable<IString, String> f) {
    List<FeatureValue<String>> blist = new LinkedList<FeatureValue<String>>();

    if (doSource) {
      int foreignPhraseSz = f.sourcePhrase.size();
      int sourceMax = Math.min(size, foreignPhraseSz);
      for (int i = 0; i < sourceMax; i++) {
        Sequence<IString> sourceB = f.sourcePhrase.subsequence(0, i + 1);
        blist.add(new FeatureValue<String>(FEATURE_PREFIX + PREFIX_L
            + PREFIX_SRC + ":" + sourceB.toString("_"), 1.0));
      }
      int sourceMin = Math.max(0, foreignPhraseSz - size);

      for (int i = foreignPhraseSz - 1; i >= sourceMin; i--) {
        Sequence<IString> sourceB = f.sourcePhrase.subsequence(i,
            foreignPhraseSz);
        blist.add(new FeatureValue<String>(FEATURE_PREFIX + PREFIX_R
            + PREFIX_SRC + ":" + sourceB.toString("_"), 1.0));
      }
    }

    if (doTarget) {
      int translationPhraseSz = f.targetPhrase.size();
      int targetMax = Math.min(size, translationPhraseSz);
      for (int i = 0; i < targetMax; i++) {
        Sequence<IString> targetB = f.targetPhrase.subsequence(0, i + 1);
        blist.add(new FeatureValue<String>(FEATURE_PREFIX + PREFIX_L
            + PREFIX_TRG + ":" + targetB.toString("_"), 1.0));
      }

      int targetMin = Math.max(0, translationPhraseSz - size);
      for (int i = translationPhraseSz - 1; i >= targetMin; i--) {
        Sequence<IString> targetB = f.targetPhrase.subsequence(i,
            translationPhraseSz);
        blist.add(new FeatureValue<String>(FEATURE_PREFIX + PREFIX_R
            + PREFIX_TRG + ":" + targetB.toString("_"), 1.0));
      }
    }
    return blist;
  }

  public void reset() {
  }
  
  @Override
  public void initialize() {
  }
}